#!/usr/bin/env python3
"""Single-file automatic pre-pump scanner for crypto perpetual futures.

Features
- Fully self-contained in one file.
- Auto-runs on startup: self-test -> continuous scan loop.
- Scans Binance USDT-M symbols (all/list/top modes).
- Builds microstructure-style features and PPS score.
- Ranks symbols most likely to move up (bullish pre-pump candidates).
- Works even without ccxt by falling back to synthetic demo mode.

Usage
    python pre_pump_auto.py

Optional environment variables
    SCAN_MODE=all                 # all | list | top
    SYMBOLS=BTC/USDT,ETH/USDT     # used when SCAN_MODE=list
    TOP_N=40                      # used when SCAN_MODE=top
    TIMEFRAME=1m
    LIMIT=240
    INTERVAL_SECONDS=45
    MAX_SYMBOLS_PER_CYCLE=120     # protective cap in all/top mode
    TOP_RESULTS=25                # rows printed each cycle
    DATA_MODE=auto                # auto | live | synthetic
"""

from __future__ import annotations

import os
import random
import time
import traceback
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Dict, List, Optional, Sequence, Tuple

try:
    import ccxt
except Exception:
    ccxt = None


# -------------------------------
# Runtime configuration
# -------------------------------
SCAN_MODE = os.getenv("SCAN_MODE", "all").lower()  # all | list | top
SYMBOLS = [s.strip() for s in os.getenv("SYMBOLS", "BTC/USDT,ETH/USDT").split(",") if s.strip()]
TOP_N = int(os.getenv("TOP_N", "40"))
TIMEFRAME = os.getenv("TIMEFRAME", "1m")
LIMIT = int(os.getenv("LIMIT", "240"))
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "45"))
MAX_SYMBOLS_PER_CYCLE = int(os.getenv("MAX_SYMBOLS_PER_CYCLE", "120"))
TOP_RESULTS = int(os.getenv("TOP_RESULTS", "25"))
DATA_MODE = os.getenv("DATA_MODE", "auto").lower()  # auto | live | synthetic
EXCHANGE_TIMEOUT_MS = int(os.getenv("EXCHANGE_TIMEOUT_MS", "15000"))
SYMBOL_PROGRESS_EVERY = int(os.getenv("SYMBOL_PROGRESS_EVERY", "10"))


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
            object.__setattr__(
                self,
                "weights",
                {
                    "f1_funding": 0.14,
                    "f2_oi_delta": 0.14,
                    "f4_cvd_slope": 0.10,
                    "f5_ofi": 0.12,
                    "f6_vol_compression": 0.10,
                    "f7_depth_ratio": 0.10,
                    "f8_spot_futures_div": 0.10,
                    "f9_liq_cluster": 0.10,
                    "f10_whale_flow": 0.10,
                },
            )


@dataclass(frozen=True)
class DetectionResult:
    symbol: str
    features: Dict[str, float]
    normalized: Dict[str, float]
    pps: float
    regime: str
    decision_tree_state: str
    pump_type: str
    bullish_score: float


def log(msg: str) -> None:
    print(msg, flush=True)


# -------------------------------
# Math helpers
# -------------------------------
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
        tr = max(curr.high - curr.low, abs(curr.high - prev_close), abs(curr.low - prev_close))
        trs.append(tr)
    return mean(trs) if trs else 0.0


def _linear_slope(values: Sequence[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2.0
    y_mean = mean(values)
    num = 0.0
    den = 0.0
    for i, y in enumerate(values):
        dx = i - x_mean
        num += dx * (y - y_mean)
        den += dx * dx
    return _safe_div(num, den)


# -------------------------------
# Feature engineering and scoring
# -------------------------------
def compute_features(bars: Sequence[MarketBar], cfg: EngineConfig) -> Dict[str, float]:
    if len(bars) < max(10, cfg.oi_delta_window_bars + 1):
        raise ValueError("Insufficient bars for feature computation")

    latest = bars[-1]

    funding_hist = [b.funding_rate for b in bars[-cfg.funding_window_bars :]]
    fr_mu = mean(funding_hist)
    fr_sigma = pstdev(funding_hist) if len(funding_hist) > 1 else 0.0
    funding_z = _safe_div(latest.funding_rate - fr_mu, fr_sigma) if fr_sigma > 0 else 0.0

    prev_oi = bars[-1 - cfg.oi_delta_window_bars].open_interest
    oi_delta_5m = _safe_div(latest.open_interest - prev_oi, prev_oi)

    oi_hist = [b.open_interest for b in bars[-min(len(bars), 30 * 24 * 60) :]]
    oi_percentile = _safe_div(sum(1 for x in oi_hist if x <= latest.open_interest), len(oi_hist))

    lookback = bars[-cfg.oi_delta_window_bars :]
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

    ofi = _safe_div(
        latest.market_buy_volume - latest.market_sell_volume,
        latest.market_buy_volume + latest.market_sell_volume,
    )

    atr_fast = _atr(bars, cfg.atr_fast_bars)
    atr_slow = _atr(bars, cfg.atr_slow_bars)
    volatility_compression = _safe_div(atr_fast, atr_slow)

    current_depth = latest.bid_depth_top + latest.ask_depth_top
    depth_hist = [b.bid_depth_top + b.ask_depth_top for b in bars[-min(len(bars), 30 * 24 * 60) :]]
    depth_ratio = _safe_div(current_depth, mean(depth_hist))

    spot_delta = _safe_div(latest.spot_volume - bars[-2].spot_volume, max(1.0, bars[-2].spot_volume))
    fut_delta = _safe_div(latest.futures_volume - bars[-2].futures_volume, max(1.0, bars[-2].futures_volume))
    spot_futures_divergence = spot_delta - fut_delta

    breakout_velocity = _safe_div(
        latest.close - bars[-1 - cfg.oi_delta_window_bars].close,
        bars[-1 - cfg.oi_delta_window_bars].close,
    )

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
        "f6_vol_compression": _clip_01(
            1.0 - _safe_div(features["volatility_compression"], cfg.volatility_compression_threshold)
        ),
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


def bullish_score(result_pps: float, features: Dict[str, float], state: str, regime: str) -> float:
    score = result_pps
    if state == "HIGH_SHORT_SQUEEZE_PROBABILITY":
        score += 0.20
    elif state == "HIDDEN_ACCUMULATION":
        score += 0.12

    if regime == "HIGH_PROBABILITY_PUMP":
        score += 0.15
    elif regime == "WATCHLIST":
        score += 0.05

    score += 0.05 * max(0.0, features["ofi"])  # buy aggression
    score += 0.05 * max(0.0, features["oi_delta_5m"])  # OI expansion
    score += 0.05 * max(0.0, -features["funding_z"])  # crowded shorts squeeze setup
    return score


def evaluate_symbol(symbol: str, bars: Sequence[MarketBar], cfg: EngineConfig) -> DetectionResult:
    features = compute_features(bars, cfg)
    normalized = normalize_features(features, cfg)
    pps = compute_pps(normalized, cfg)
    regime = classify_regime(pps, cfg)
    state = decision_tree_state(features, cfg)
    ptype = classify_pump_type(features, cfg)
    bscore = bullish_score(pps, features, state, regime)
    return DetectionResult(symbol, features, normalized, pps, regime, state, ptype, bscore)


# -------------------------------
# Data providers
# -------------------------------
def create_exchange():
    if ccxt is None:
        raise RuntimeError("ccxt is not installed")
    return ccxt.binanceusdm({"enableRateLimit": True, "timeout": EXCHANGE_TIMEOUT_MS, "options": {"defaultType": "future"}})


def fetch_all_usdtm_symbols(exchange) -> List[str]:
    markets = exchange.load_markets()
    symbols: List[str] = []
    for m in markets.values():
        if m.get("linear") and m.get("quote") == "USDT" and m.get("contract"):
            symbols.append(m["symbol"])
    return sorted(symbols)


def _fetch_open_interest_map(exchange, symbol: str) -> Dict[int, float]:
    try:
        hist = exchange.fetch_open_interest_history(symbol, timeframe=TIMEFRAME, limit=LIMIT)
        mp: Dict[int, float] = {}
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
        return float((exchange.fetch_funding_rate(symbol) or {}).get("fundingRate") or 0.0)
    except Exception:
        return 0.0


def _fetch_depth(exchange, symbol: str) -> Tuple[float, float]:
    try:
        ob = exchange.fetch_order_book(symbol, 20)
        bid = sum(float(x[1]) for x in ob.get("bids", [])[:10])
        ask = sum(float(x[1]) for x in ob.get("asks", [])[:10])
        return bid, ask
    except Exception:
        return 0.0, 0.0


def _fetch_recent_trade_split(exchange, symbol: str) -> Tuple[float, float]:
    try:
        trades = exchange.fetch_trades(symbol, limit=200)
        buy_vol = 0.0
        sell_vol = 0.0
        for t in trades:
            amt = float(t.get("amount") or 0.0)
            side = str(t.get("side") or "").lower()
            if side == "buy":
                buy_vol += amt
            elif side == "sell":
                sell_vol += amt
        return buy_vol, sell_vol
    except Exception:
        return 0.0, 0.0


def build_market_bars_live(exchange, symbol: str) -> List[MarketBar]:
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=LIMIT)
    oi_map = _fetch_open_interest_map(exchange, symbol)
    funding_now = _fetch_funding_rate(exchange, symbol)
    bid_depth, ask_depth = _fetch_depth(exchange, symbol)
    buy_v, sell_v = _fetch_recent_trade_split(exchange, symbol)

    bars: List[MarketBar] = []
    for i, row in enumerate(ohlcv):
        ts, _o, h, l, c, v = row
        oi = oi_map.get(int(ts), 0.0)
        mbuy = (buy_v / max(1, len(ohlcv))) if i == len(ohlcv) - 1 else float(v) * 0.5
        msell = (sell_v / max(1, len(ohlcv))) if i == len(ohlcv) - 1 else float(v) * 0.5
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


def build_market_bars_synthetic(symbol: str, n: int = 240) -> List[MarketBar]:
    seed = abs(hash(symbol)) % (2**31 - 1)
    rng = random.Random(seed)
    price = 100.0 + rng.random() * 50
    oi_base = 1_000_000 + rng.random() * 500_000
    bars: List[MarketBar] = []
    ts0 = int(time.time() * 1000) - n * 60_000

    for i in range(n):
        noise = rng.uniform(-0.002, 0.002)
        drift = 0.0002 if rng.random() > 0.55 else -0.0001
        price *= 1.0 + noise + drift

        high = price * (1 + abs(rng.uniform(0, 0.0015)))
        low = price * (1 - abs(rng.uniform(0, 0.0015)))
        close = price

        vol = 1000 + abs(rng.gauss(0, 200))
        buy = vol * rng.uniform(0.45, 0.62)
        sell = max(1.0, vol - buy)

        oi = oi_base + i * rng.uniform(50, 500)
        funding = rng.uniform(-0.0015, 0.001)
        bid_depth = 150_000 + abs(rng.gauss(0, 30_000))
        ask_depth = 150_000 + abs(rng.gauss(0, 30_000))

        bars.append(
            MarketBar(
                timestamp_ms=ts0 + i * 60_000,
                high=high,
                low=low,
                close=close,
                volume=vol,
                market_buy_volume=buy,
                market_sell_volume=sell,
                open_interest=oi,
                funding_rate=funding,
                bid_depth_top=bid_depth,
                ask_depth_top=ask_depth,
                spot_volume=vol,
                futures_volume=vol,
                liquidation_cluster_density=rng.uniform(0.3, 0.9),
                whale_flow_score_raw=rng.uniform(0.3, 0.95),
            )
        )

    # Inject pump-ready signature near end
    for j in range(5):
        idx = n - 5 + j
        b = bars[idx]
        bars[idx] = MarketBar(
            timestamp_ms=b.timestamp_ms,
            high=b.close * 1.001,
            low=b.close * 0.999,
            close=b.close * (1 + 0.0008 * j),
            volume=b.volume * 1.2,
            market_buy_volume=b.market_buy_volume * 1.4,
            market_sell_volume=b.market_sell_volume * 0.8,
            open_interest=b.open_interest * (1 + 0.01 * j),
            funding_rate=min(-0.0020, b.funding_rate - 0.0004),
            bid_depth_top=b.bid_depth_top * 0.65,
            ask_depth_top=b.ask_depth_top * 0.65,
            spot_volume=b.spot_volume * 1.2,
            futures_volume=b.futures_volume * 1.2,
            liquidation_cluster_density=min(1.0, b.liquidation_cluster_density + 0.15),
            whale_flow_score_raw=min(1.0, b.whale_flow_score_raw + 0.12),
        )
    return bars


# -------------------------------
# Self-test and output formatting
# -------------------------------
def run_self_test() -> None:
    cfg = EngineConfig(funding_window_bars=60, atr_slow_bars=60)
    bars = build_market_bars_synthetic("SELFTEST/USDT", n=120)
    res = evaluate_symbol("SELFTEST/USDT", bars, cfg)
    if res.pps < cfg.pps_watch_threshold:
        raise RuntimeError(f"Self-test failed: PPS too low ({res.pps:.3f})")


def _row(r: DetectionResult) -> str:
    return (
        f"{r.symbol:<14} | bull={r.bullish_score:>5.3f} | pps={r.pps:>5.3f} | "
        f"{r.regime:<22} | {r.decision_tree_state:<30} | "
        f"fundZ={r.features['funding_z']:>6.2f} oi5m={r.features['oi_delta_5m']:>6.3f} "
        f"ofi={r.features['ofi']:>6.3f} depth={r.features['depth_ratio']:>6.3f}"
    )


def _select_universe(exchange, mode: str) -> List[str]:
    if mode == "list":
        return SYMBOLS
    all_symbols = fetch_all_usdtm_symbols(exchange) if exchange is not None else []
    if mode == "top":
        return all_symbols[:TOP_N]
    return all_symbols


# -------------------------------
# Main loop
# -------------------------------
def main() -> None:
    log("[BOOT] running self-test...")
    run_self_test()
    log("[BOOT] self-test passed.")

    use_live = (DATA_MODE in {"auto", "live"}) and ccxt is not None
    exchange = None

    if use_live:
        try:
            exchange = create_exchange()
            log("[BOOT] live mode enabled (Binance USDT-M).")
        except Exception as exc:
            if DATA_MODE == "live":
                raise
            log(f"[WARN] could not initialize live mode: {exc}")
            log("[WARN] fallback to synthetic mode.")
            use_live = False
    else:
        log("[BOOT] synthetic mode enabled.")

    cfg = EngineConfig()

    while True:
        start_ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        log(f"\n[SCAN] {start_ts} UTC")

        if use_live:
            log(f"[STEP] loading symbol universe (mode={SCAN_MODE}) ...")
            universe = _select_universe(exchange, SCAN_MODE)
            log(f"[STEP] universe loaded: {len(universe)} symbols")
            if not universe:
                log("[WARN] empty universe from exchange; sleeping...")
                time.sleep(INTERVAL_SECONDS)
                continue
        else:
            universe = SYMBOLS if SCAN_MODE == "list" else [f"SYN{i}/USDT" for i in range(1, MAX_SYMBOLS_PER_CYCLE + 1)]

        if len(universe) > MAX_SYMBOLS_PER_CYCLE:
            universe = universe[:MAX_SYMBOLS_PER_CYCLE]

        results: List[DetectionResult] = []
        errors = 0

        for i, symbol in enumerate(universe, start=1):
            if i == 1 or i % max(1, SYMBOL_PROGRESS_EVERY) == 0:
                log(f"[PROGRESS] processing {i}/{len(universe)}: {symbol}")
            try:
                bars = build_market_bars_live(exchange, symbol) if use_live else build_market_bars_synthetic(symbol, n=LIMIT)
                if len(bars) < max(20, cfg.oi_delta_window_bars + 2):
                    continue
                results.append(evaluate_symbol(symbol, bars, cfg))
            except Exception as exc:
                errors += 1
                if errors <= 5:
                    log(f"[ERROR] {symbol}: {exc}")

        if not results:
            log("[WARN] no valid results this cycle.")
            time.sleep(INTERVAL_SECONDS)
            continue

        # Rank symbols likely to rise (bullish pre-pump candidates)
        ranked = sorted(results, key=lambda r: r.bullish_score, reverse=True)

        log(f"[INFO] scanned={len(results)} symbols, errors={errors}, showing top={min(TOP_RESULTS, len(ranked))}")
        log("-" * 175)
        for r in ranked[:TOP_RESULTS]:
            log(_row(r))
        log("-" * 175)

        high_conf = [r for r in ranked if r.regime == "HIGH_PROBABILITY_PUMP"]
        watch = [r for r in ranked if r.regime == "WATCHLIST"]
        log(f"[SUMMARY] high_conf={len(high_conf)} watchlist={len(watch)} no_signal={len(ranked)-len(high_conf)-len(watch)}")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\nStopped by user.")
    except Exception:
        log(traceback.format_exc())
        raise
