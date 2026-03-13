"""Pre-pump detection engine for crypto perpetual futures.

Implements the microstructure framework as executable Python logic:
- Feature engineering (funding z-score, OI delta, CVD slope, OFI, volatility compression, depth ratio...)
- Composite Pump Preparation Score (PPS)
- Decision-tree diagnostics
- Pump type classification

Input data model is bar-based and intentionally exchange-agnostic.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Dict, List, Optional, Sequence


@dataclass(frozen=True)
class MarketBar:
    """Aggregated market data for one interval (e.g., 1m or 5m)."""

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
    """Thresholds, rolling windows, and weights for the PPS model."""

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

    weights: Dict[str, float] = None  # type: ignore[assignment]

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
    """Outputs from a full evaluation cycle."""

    features: Dict[str, float]
    normalized: Dict[str, float]
    pps: float
    regime: str
    decision_tree_state: str
    pump_type: str


# ---------- Utility math ----------


def _safe_div(a: float, b: float) -> float:
    if b == 0:
        return 0.0
    return a / b


def _clip_01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _atr(bars: Sequence[MarketBar], period: int) -> float:
    if len(bars) < 2:
        return 0.0
    n = min(period, len(bars) - 1)
    if n <= 0:
        return 0.0

    trs: List[float] = []
    start = len(bars) - n
    for i in range(start, len(bars)):
        curr = bars[i]
        prev_close = bars[i - 1].close
        tr = max(
            curr.high - curr.low,
            abs(curr.high - prev_close),
            abs(curr.low - prev_close),
        )
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


# ---------- Feature engineering ----------


def compute_features(bars: Sequence[MarketBar], cfg: Optional[EngineConfig] = None) -> Dict[str, float]:
    """Compute raw features from a list of bars.

    The latest bar is considered the "current" observation.
    """
    cfg = cfg or EngineConfig()
    if len(bars) < max(10, cfg.oi_delta_window_bars + 1):
        raise ValueError("Insufficient bars for feature computation")

    latest = bars[-1]

    # F1 Funding z-score
    funding_hist = [b.funding_rate for b in bars[-cfg.funding_window_bars :]]
    fr_mu = mean(funding_hist)
    fr_sigma = pstdev(funding_hist) if len(funding_hist) > 1 else 0.0
    funding_z = _safe_div(latest.funding_rate - fr_mu, fr_sigma) if fr_sigma > 0 else 0.0

    # F2 OI 5m delta
    prev_oi = bars[-1 - cfg.oi_delta_window_bars].open_interest
    oi_delta_5m = _safe_div(latest.open_interest - prev_oi, prev_oi)

    # F3 OI percentile (rolling)
    oi_hist = [b.open_interest for b in bars[-min(len(bars), 30 * 24 * 60) :]]
    oi_less_equal = sum(1 for x in oi_hist if x <= latest.open_interest)
    oi_percentile = _safe_div(oi_less_equal, len(oi_hist))

    # Price compression over last 5 bars
    lookback = bars[-cfg.oi_delta_window_bars :]
    high_5m = max(b.high for b in lookback)
    low_5m = min(b.low for b in lookback)
    mid = (high_5m + low_5m) / 2.0
    price_range_5m = _safe_div(high_5m - low_5m, mid)

    # CVD and slope
    cvd_series: List[float] = []
    cumulative = 0.0
    for b in bars[-60:]:
        cumulative += b.market_buy_volume - b.market_sell_volume
        cvd_series.append(cumulative)
    cvd_slope = _linear_slope(cvd_series)

    # OFI
    ofi = _safe_div(
        latest.market_buy_volume - latest.market_sell_volume,
        latest.market_buy_volume + latest.market_sell_volume,
    )

    # Volatility compression (ATR fast / ATR slow)
    atr_fast = _atr(bars, cfg.atr_fast_bars)
    atr_slow = _atr(bars, cfg.atr_slow_bars)
    volatility_compression = _safe_div(atr_fast, atr_slow)

    # Depth ratio
    current_depth = latest.bid_depth_top + latest.ask_depth_top
    depth_hist = [b.bid_depth_top + b.ask_depth_top for b in bars[-min(len(bars), 30 * 24 * 60) :]]
    avg_depth = mean(depth_hist)
    depth_ratio = _safe_div(current_depth, avg_depth)

    # Spot/futures divergence
    spot_delta = _safe_div(
        latest.spot_volume - bars[-2].spot_volume,
        max(1.0, bars[-2].spot_volume),
    )
    fut_delta = _safe_div(
        latest.futures_volume - bars[-2].futures_volume,
        max(1.0, bars[-2].futures_volume),
    )
    spot_futures_divergence = spot_delta - fut_delta

    # Breakout velocity proxy (close change over 5 bars)
    breakout_velocity = _safe_div(latest.close - bars[-1 - cfg.oi_delta_window_bars].close, bars[-1 - cfg.oi_delta_window_bars].close)

    # Squeeze score
    fr_negative_component = abs(min(funding_z, 0.0))
    squeeze_score = fr_negative_component + oi_percentile + max(0.0, breakout_velocity)

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


def normalize_features(features: Dict[str, float], cfg: Optional[EngineConfig] = None) -> Dict[str, float]:
    """Normalize raw features to [0,1] domain for PPS."""
    cfg = cfg or EngineConfig()
    return {
        # More negative funding_z is more bullish for short squeeze setup.
        "f1_funding": _clip_01(_safe_div(-features["funding_z"], 3.0)),
        "f2_oi_delta": _clip_01(_safe_div(features["oi_delta_5m"], cfg.oi_delta_threshold)),
        "f4_cvd_slope": _clip_01(0.5 + features["cvd_slope"]),
        "f5_ofi": _clip_01(0.5 + features["ofi"]),
        # Lower compression ratio = stronger setup, hence inverse.
        "f6_vol_compression": _clip_01(1.0 - _safe_div(features["volatility_compression"], cfg.volatility_compression_threshold)),
        # Lower depth ratio = thinner book = higher pump fragility.
        "f7_depth_ratio": _clip_01(1.0 - _safe_div(features["depth_ratio"], cfg.depth_fragile_threshold)),
        "f8_spot_futures_div": _clip_01(0.5 + features["spot_futures_divergence"]),
        "f9_liq_cluster": _clip_01(features["liquidation_cluster_density"]),
        "f10_whale_flow": _clip_01(features["whale_flow_score"]),
    }


def compute_pps(normalized: Dict[str, float], cfg: Optional[EngineConfig] = None) -> float:
    """Composite Pump Preparation Score."""
    cfg = cfg or EngineConfig()
    return sum(cfg.weights[k] * normalized.get(k, 0.0) for k in cfg.weights)


def classify_regime(pps: float, cfg: Optional[EngineConfig] = None) -> str:
    cfg = cfg or EngineConfig()
    if pps > cfg.pps_high_threshold:
        return "HIGH_PROBABILITY_PUMP"
    if pps >= cfg.pps_watch_threshold:
        return "WATCHLIST"
    return "NO_SIGNAL"


def decision_tree_state(features: Dict[str, float], cfg: Optional[EngineConfig] = None) -> str:
    """Implement decision logic from the research framework."""
    cfg = cfg or EngineConfig()

    vol_compressed = features["volatility_compression"] < cfg.volatility_compression_threshold
    oi_rising_fast = features["oi_delta_5m"] > cfg.oi_delta_threshold
    funding_extreme_negative = features["funding_z"] < -2.0
    hidden_accumulation = (
        features["cvd_slope"] > 0
        and features["price_range_5m"] < cfg.range_compression_threshold
        and features["oi_delta_5m"] > 0
    )

    if vol_compressed:
        if oi_rising_fast:
            if funding_extreme_negative:
                return "HIGH_SHORT_SQUEEZE_PROBABILITY"
            if hidden_accumulation:
                return "HIDDEN_ACCUMULATION"
            return "MONITOR"
    return "NO_PRE_PUMP_CONDITION"


def classify_pump_type(features: Dict[str, float], cfg: Optional[EngineConfig] = None) -> str:
    """Classify likely pump archetype from feature signatures."""
    cfg = cfg or EngineConfig()

    leverage_driven = (
        features["oi_delta_5m"] > cfg.oi_delta_threshold
        and abs(features["funding_z"]) > 2.0
        and features["spot_futures_divergence"] < 0
    )
    spot_driven = features["spot_futures_divergence"] > 0
    manipulative = (
        features["ofi"] > cfg.ofi_strong_threshold
        and features["oi_percentile"] < 0.35
        and features["depth_ratio"] < cfg.depth_fragile_threshold
    )
    accumulation = (
        features["oi_delta_5m"] > 0
        and features["price_range_5m"] < cfg.range_compression_threshold
        and features["cvd_slope"] > 0
        and abs(features["funding_z"]) < 1.0
    )

    if leverage_driven:
        return "LEVERAGE_DRIVEN_SYNTHETIC_PUMP"
    if spot_driven and features["oi_delta_5m"] <= cfg.oi_delta_threshold:
        return "SPOT_DRIVEN_ORGANIC_RALLY"
    if manipulative:
        return "MANIPULATIVE_PUMP_DUMP"
    if accumulation:
        return "INSTITUTIONAL_ACCUMULATION_PHASE"
    return "UNCLASSIFIED"


def evaluate_pre_pump(bars: Sequence[MarketBar], cfg: Optional[EngineConfig] = None) -> DetectionResult:
    """Run full pre-pump evaluation pipeline."""
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
