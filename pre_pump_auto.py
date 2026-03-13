#!/usr/bin/env python3
"""Auto-running pre-pump detection system in a single file.

What this script does when started:
1) Runs quick internal self-tests (synthetic data).
2) Connects to Binance USDT-M futures via ccxt.
3) Pulls OHLCV + public metrics (funding, open interest, order book/trades approximations).
4) Computes microstructure features and Pump Preparation Score (PPS).
5) Prints alerts continuously on configured interval.

Run:
    python pre_pump_auto.py

Optional env vars:
    SYMBOLS=BTC/USDT,ETH/USDT
    TIMEFRAME=1m
    LIMIT=300
    INTERVAL_SECONDS=30
    SCAN_MODE=list   # list|top
    TOP_N=20
"""

from __future__ import annotations

import os
import time
import traceback
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Dict, List, Optional, Sequence

try:
    import ccxt
except Exception:  # optional at runtime
    ccxt = None


# -------------------------------
# Config
# -------------------------------
TIMEFRAME = os.getenv("TIMEFRAME", "1m")
LIMIT = int(os.getenv("LIMIT", "300"))
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "30"))
SCAN_MODE = os.getenv("SCAN_MODE", "list")  # list | top
TOP_N = int(os.getenv("TOP_N", "20"))
SYMBOLS = [s.strip() for s in os.getenv("SYMBOLS", "BTC/USDT,ETH/USDT").split(",") if s.strip()]


@dataclass(frozen=True)
class MarketBar:
    timestamp_ms: int
    high: float
    low: float
    close: float
    volume: float
    market_buy_volume: float
    market_sell_volume: float
    open_interest: float
    funding_rate: float
    bid_depth_top: float
    ask_depth_top: float
    spot_volume: float = 0.0
    futures_volume: float = 0.0
    liquidation_cluster_density: float = 0.0
    whale_flow_score_raw: float = 0.0


@dataclass(frozen=True)
class EngineConfig:
    funding_window_bars: int = 7 * 24 * 60
    oi_delta_window_bars: int = 5
    range_compression_threshold: float = 0.005
    oi_delta_threshold: float = 0.03
    ofi_strong_threshold: float = 0.25
    depth_fragile_threshold: float = 0.60
    volatility_compression_threshold: float = 0.40
    atr_fast_bars: int = 5
    atr_slow_bars: int = 24 * 60
    pps_high_threshold: float = 0.75
    pps_watch_threshold: float = 0.55
    weights: Optional[Dict[str, float]] = None

    def __post_init__(self) -> None:
        if self.weights is None:
            object.__setattr__(self, "weights", {
                "f1_funding": 0.14,
                "f2_oi_delta": 0.14,
                "f4_cvd_slope": 0.10,
                "f5_ofi": 0.12,
                "f6_vol_compression": 0.10,
                "f7_depth_ratio": 0.10,
                "f8_spot_futures_div": 0.10,
                "f9_liq_cluster": 0.10,
                "f10_whale_flow": 0.10,
            })


@dataclass(frozen=True)
class DetectionResult:
    features: Dict[str, float]
    normalized: Dict[str, float]
    pps: float
    regime: str
    decision_tree_state: str
    pump_type: str


def _safe_div(a: float, b: float) -> float:
    return 0.0 if b == 0 else a / b


def _clip_01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _atr(bars: Sequence[MarketBar], period: int) -> float:
    if len(bars) < 2:
        return 0.0
    n = min(period, len(bars) - 1)
    trs: List[float] = []
    for i in range(len(bars) - n, len(bars)):
        curr = bars[i]
        prev_close = bars[i - 1].close
        trs.append(max(curr.high - curr.low, abs(curr.high - prev_close), abs(curr.low - prev_close)))
    return mean(trs) if trs else 0.0


def _linear_slope(values: Sequence[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2
    y_mean = mean(values)
    num = 0.0
    den = 0.0
    for i, y in enumerate(values):
        dx = i - x_mean
        num += dx * (y - y_mean)
        den += dx * dx
    return _safe_div(num, den)


def compute_features(bars: Sequence[MarketBar], cfg: EngineConfig) -> Dict[str, float]:
    if len(bars) < max(10, cfg.oi_delta_window_bars + 1):
        raise ValueError("Insufficient bars")

    latest = bars[-1]
    funding_hist = [b.funding_rate for b in bars[-cfg.funding_window_bars:]]
    fr_mu = mean(funding_hist)
    fr_sigma = pstdev(funding_hist) if len(funding_hist) > 1 else 0.0
    funding_z = _safe_div(latest.funding_rate - fr_mu, fr_sigma) if fr_sigma > 0 else 0.0

    prev_oi = bars[-1 - cfg.oi_delta_window_bars].open_interest
    oi_delta_5m = _safe_div(latest.open_interest - prev_oi, prev_oi)

    oi_hist = [b.open_interest for b in bars[-min(len(bars), 30 * 24 * 60):]]
    oi_percentile = _safe_div(sum(1 for x in oi_hist if x <= latest.open_interest), len(oi_hist))

    lookback = bars[-cfg.oi_delta_window_bars:]
    high_5m = max(b.high for b in lookback)
    low_5m = min(b.low for b in lookback)
    mid = (high_5m + low_5m) / 2.0
    price_range_5m = _safe_div(high_5m - low_5m, mid)

    cvd_series: List[float] = []
    cumulative = 0.0
    for b in bars[-60:]:
        cumulative += b.market_buy_volume - b.market_sell_volume
        cvd_series.append(cumulative)
    cvd_slope = _linear_slope(cvd_series)

    ofi = _safe_div(latest.market_buy_volume - latest.market_sell_volume, latest.market_buy_volume + latest.market_sell_volume)

    atr_fast = _atr(bars, cfg.atr_fast_bars)
    atr_slow = _atr(bars, cfg.atr_slow_bars)
    volatility_compression = _safe_div(atr_fast, atr_slow)

    current_depth = latest.bid_depth_top + latest.ask_depth_top
    depth_hist = [b.bid_depth_top + b.ask_depth_top for b in bars[-min(len(bars), 30 * 24 * 60):]]
    depth_ratio = _safe_div(current_depth, mean(depth_hist))

    spot_delta = _safe_div(latest.spot_volume - bars[-2].spot_volume, max(1.0, bars[-2].spot_volume))
    fut_delta = _safe_div(latest.futures_volume - bars[-2].futures_volume, max(1.0, bars[-2].futures_volume))
    spot_futures_divergence = spot_delta - fut_delta

    breakout_velocity = _safe_div(latest.close - bars[-1 - cfg.oi_delta_window_bars].close, bars[-1 - cfg.oi_delta_window_bars].close)
    squeeze_score = abs(min(funding_z, 0.0)) + oi_percentile + max(0.0, breakout_velocity)

    return {
        "funding_z": funding_z,
        "oi_delta_5m": oi_delta_5m,
        "oi_percentile": oi_percentile,
        "price_range_5m": price_range_5m,
        "cvd_slope": cvd_slope,
        "ofi": ofi,
        "volatility_compression": volatility_compression,
        "depth_ratio": depth_ratio,
        "spot_futures_divergence": spot_futures_divergence,
        "liquidation_cluster_density": latest.liquidation_cluster_density,
        "whale_flow_score": latest.whale_flow_score_raw,
        "breakout_velocity": breakout_velocity,
        "squeeze_score": squeeze_score,
    }


def normalize_features(features: Dict[str, float], cfg: EngineConfig) -> Dict[str, float]:
    return {
        "f1_funding": _clip_01(_safe_div(-features["funding_z"], 3.0)),
        "f2_oi_delta": _clip_01(_safe_div(features["oi_delta_5m"], cfg.oi_delta_threshold)),
        "f4_cvd_slope": _clip_01(0.5 + features["cvd_slope"]),
        "f5_ofi": _clip_01(0.5 + features["ofi"]),
        "f6_vol_compression": _clip_01(1.0 - _safe_div(features["volatility_compression"], cfg.volatility_compression_threshold)),
        "f7_depth_ratio": _clip_01(1.0 - _safe_div(features["depth_ratio"], cfg.depth_fragile_threshold)),
        "f8_spot_futures_div": _clip_01(0.5 + features["spot_futures_divergence"]),
        "f9_liq_cluster": _clip_01(features["liquidation_cluster_density"]),
        "f10_whale_flow": _clip_01(features["whale_flow_score"]),
    }


def compute_pps(normalized: Dict[str, float], cfg: EngineConfig) -> float:
    return sum(cfg.weights[k] * normalized.get(k, 0.0) for k in cfg.weights)


def classify_regime(pps: float, cfg: EngineConfig) -> str:
    if pps > cfg.pps_high_threshold:
        return "HIGH_PROBABILITY_PUMP"
    if pps >= cfg.pps_watch_threshold:
        return "WATCHLIST"
    return "NO_SIGNAL"


def decision_tree_state(features: Dict[str, float], cfg: EngineConfig) -> str:
    if features["volatility_compression"] < cfg.volatility_compression_threshold:
        if features["oi_delta_5m"] > cfg.oi_delta_threshold:
            if features["funding_z"] < -2.0:
                return "HIGH_SHORT_SQUEEZE_PROBABILITY"
            if (
                features["cvd_slope"] > 0
                and features["price_range_5m"] < cfg.range_compression_threshold
                and features["oi_delta_5m"] > 0
            ):
                return "HIDDEN_ACCUMULATION"
            return "MONITOR"
    return "NO_PRE_PUMP_CONDITION"


def classify_pump_type(features: Dict[str, float], cfg: EngineConfig) -> str:
    if (
        features["oi_delta_5m"] > cfg.oi_delta_threshold
        and abs(features["funding_z"]) > 2.0
        and features["spot_futures_divergence"] < 0
    ):
        return "LEVERAGE_DRIVEN_SYNTHETIC_PUMP"
    if features["spot_futures_divergence"] > 0 and features["oi_delta_5m"] <= cfg.oi_delta_threshold:
        return "SPOT_DRIVEN_ORGANIC_RALLY"
    if (
        features["ofi"] > cfg.ofi_strong_threshold
        and features["oi_percentile"] < 0.35
        and features["depth_ratio"] < cfg.depth_fragile_threshold
    ):
        return "MANIPULATIVE_PUMP_DUMP"
    if (
        features["oi_delta_5m"] > 0
        and features["price_range_5m"] < cfg.range_compression_threshold
        and features["cvd_slope"] > 0
        and abs(features["funding_z"]) < 1.0
    ):
        return "INSTITUTIONAL_ACCUMULATION_PHASE"
    return "UNCLASSIFIED"


def evaluate_pre_pump(bars: Sequence[MarketBar], cfg: Optional[EngineConfig] = None) -> DetectionResult:
    cfg = cfg or EngineConfig()
    features = compute_features(bars, cfg)
    normalized = normalize_features(features, cfg)
    pps = compute_pps(normalized, cfg)
    return DetectionResult(
        features=features,
        normalized=normalized,
        pps=pps,
        regime=classify_regime(pps, cfg),
        decision_tree_state=decision_tree_state(features, cfg),
        pump_type=classify_pump_type(features, cfg),
    )


def create_exchange():
    if ccxt is None:
        raise RuntimeError("ccxt is not installed. Install with: pip install ccxt")
    return ccxt.binanceusdm({"enableRateLimit": True, "options": {"defaultType": "future"}})


def fetch_symbols(exchange) -> List[str]:
    markets = exchange.load_markets()
    futs = []
    for m in markets.values():
        if m.get("linear") and m.get("quote") == "USDT" and m.get("contract"):
            futs.append(m["symbol"])
    return sorted(futs)


def _fetch_open_interest_map(exchange, symbol: str) -> Dict[int, float]:
    try:
        hist = exchange.fetch_open_interest_history(symbol, timeframe=TIMEFRAME, limit=LIMIT)
        mp = {}
        for r in hist:
            ts = r.get("timestamp")
            oi = r.get("openInterestAmount") or r.get("openInterestValue") or r.get("openInterest")
            if ts is not None and oi is not None:
                mp[int(ts)] = float(oi)
        return mp
    except Exception:
        return {}


def _fetch_funding_rate(exchange, symbol: str) -> float:
    try:
        fr = exchange.fetch_funding_rate(symbol)
        return float(fr.get("fundingRate") or 0.0)
    except Exception:
        return 0.0


def _fetch_depth(exchange, symbol: str) -> tuple[float, float]:
    try:
        ob = exchange.fetch_order_book(symbol, 20)
        bid = sum(float(x[1]) for x in ob.get("bids", [])[:10])
        ask = sum(float(x[1]) for x in ob.get("asks", [])[:10])
        return bid, ask
    except Exception:
        return 0.0, 0.0


def _fetch_recent_trade_split(exchange, symbol: str) -> tuple[float, float]:
    try:
        trades = exchange.fetch_trades(symbol, limit=200)
        buy_vol = 0.0
        sell_vol = 0.0
        for t in trades:
            amount = float(t.get("amount") or 0.0)
            side = (t.get("side") or "").lower()
            if side == "buy":
                buy_vol += amount
            elif side == "sell":
                sell_vol += amount
        return buy_vol, sell_vol
    except Exception:
        return 0.0, 0.0


def build_market_bars(exchange, symbol: str) -> List[MarketBar]:
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=LIMIT)
    oi_map = _fetch_open_interest_map(exchange, symbol)
    funding_now = _fetch_funding_rate(exchange, symbol)
    bid_depth, ask_depth = _fetch_depth(exchange, symbol)
    buy_v, sell_v = _fetch_recent_trade_split(exchange, symbol)

    bars: List[MarketBar] = []
    for i, row in enumerate(ohlcv):
        ts, _o, h, l, c, v = row
        oi = oi_map.get(int(ts), oi_map.get(int(ts // 1000 * 1000), 0.0))
        mbuy = (buy_v / max(1, len(ohlcv))) if i == len(ohlcv) - 1 else v * 0.5
        msell = (sell_v / max(1, len(ohlcv))) if i == len(ohlcv) - 1 else v * 0.5
        bars.append(
            MarketBar(
                timestamp_ms=int(ts),
                high=float(h),
                low=float(l),
                close=float(c),
                volume=float(v),
                market_buy_volume=float(mbuy),
                market_sell_volume=float(msell),
                open_interest=float(oi),
                funding_rate=float(funding_now),
                bid_depth_top=float(bid_depth),
                ask_depth_top=float(ask_depth),
                spot_volume=float(v),
                futures_volume=float(v),
                liquidation_cluster_density=0.5,
                whale_flow_score_raw=0.5,
            )
        )
    return bars


def run_self_test() -> None:
    bars: List[MarketBar] = []
    for i in range(120):
        bars.append(
            MarketBar(
                timestamp_ms=i * 60_000,
                high=100.2,
                low=99.8,
                close=100.0,
                volume=1000,
                market_buy_volume=700,
                market_sell_volume=500,
                open_interest=1_000_000 + i * 100,
                funding_rate=-0.0001,
                bid_depth_top=200_000,
                ask_depth_top=200_000,
                spot_volume=10_000_000 + i * 1000,
                futures_volume=12_000_000 + i * 1200,
                liquidation_cluster_density=0.4,
                whale_flow_score_raw=0.4,
            )
        )

    for j in range(5):
        idx = 115 + j
        bars[idx] = MarketBar(
            timestamp_ms=idx * 60_000,
            high=100.1,
            low=99.95,
            close=100.0 + j * 0.01,
            volume=1200,
            market_buy_volume=950,
            market_sell_volume=350,
            open_interest=1_000_000 + j * 20_000,
            funding_rate=-0.0025,
            bid_depth_top=70_000,
            ask_depth_top=70_000,
            spot_volume=10_000_000 + idx * 1000,
            futures_volume=12_000_000 + idx * 1200,
            liquidation_cluster_density=0.9,
            whale_flow_score_raw=0.85,
        )

    result = evaluate_pre_pump(bars, EngineConfig(funding_window_bars=60, atr_slow_bars=60))
    if result.pps < 0.55:
        raise RuntimeError("Self-test failed: PPS unexpectedly low")


def format_alert(symbol: str, result: DetectionResult) -> str:
    return (
        f"{symbol:<12} | PPS={result.pps:.3f} | {result.regime:<22} | "
        f"{result.decision_tree_state:<30} | {result.pump_type:<35} | "
        f"funding_z={result.features['funding_z']:.2f} oiΔ5m={result.features['oi_delta_5m']:.3f} "
        f"ofi={result.features['ofi']:.3f} depth={result.features['depth_ratio']:.3f}"
    )


def main() -> None:
    print("[BOOT] running self-test...")
    run_self_test()
    print("[BOOT] self-test passed. starting scanner...")

    exchange = create_exchange()
    cfg = EngineConfig()

    if SCAN_MODE == "top":
        universe = fetch_symbols(exchange)[:TOP_N]
    else:
        universe = SYMBOLS

    while True:
        started = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        print(f"\n[SCAN] {started} UTC")
        for symbol in universe:
            try:
                bars = build_market_bars(exchange, symbol)
                if len(bars) < 20:
                    print(f"{symbol:<12} | insufficient bars")
                    continue
                result = evaluate_pre_pump(bars, cfg)
                if result.regime != "NO_SIGNAL" or result.decision_tree_state != "NO_PRE_PUMP_CONDITION":
                    print("ALERT -> " + format_alert(symbol, result))
                else:
                    print("INFO  -> " + format_alert(symbol, result))
            except Exception as exc:
                print(f"ERROR -> {symbol:<12} | {exc}")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception:
        print(traceback.format_exc())
        raise
