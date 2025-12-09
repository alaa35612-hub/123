# pip install ccxt pandas numpy
"""Bollinger Band scanner for Binance USDT-M futures.
This script uses ccxt to fetch OHLCV data and evaluates two strategies
based on three Bollinger Bands (sources: High, Low, Close).
"""
import time
from typing import Dict, List

import ccxt
import numpy as np
import pandas as pd

# === Configurable settings ===
TIMEFRAME = "15m"  # e.g., "5m", "15m", "1h"
LOOKBACK_CANDLES = 400  # number of candles to request for calculations
SLEEP_SECONDS = 60  # delay between scans
BB_LENGTH = 50
BB_STD = 2
N_TREND_CONTINUE = 5  # candles to confirm the trend is still intact
M_TREND_END = 2  # candles to confirm the trend has likely ended

# === Exchange setup ===
exchange = ccxt.binanceusdm({
    "enableRateLimit": True,
    "options": {
        "defaultType": "future",
    },
})


def fetch_usdtm_symbols() -> List[str]:
    """Return list of USDT-M perpetual futures symbols."""
    markets = exchange.load_markets()
    symbols = []
    for info in markets.values():
        if not info.get("linear"):
            continue
        if info.get("contractType") != "perpetual":
            continue
        if info.get("quote") != "USDT":
            continue
        symbols.append(info["symbol"])
    return sorted(symbols)


def compute_bollinger(source: pd.Series) -> Dict[str, pd.Series]:
    """Compute Bollinger Bands for a given price source."""
    basis = source.rolling(BB_LENGTH).mean()
    std = source.rolling(BB_LENGTH).std(ddof=0)
    upper = basis + BB_STD * std
    lower = basis - BB_STD * std
    return {
        "basis": basis,
        "upper": upper,
        "lower": lower,
    }


def prepare_dataframe(ohlcv: List[List[float]]) -> pd.DataFrame:
    """Convert OHLCV list to a pandas DataFrame with Bollinger calculations."""
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    bb_high = compute_bollinger(df["high"])
    bb_low = compute_bollinger(df["low"])
    bb_close = compute_bollinger(df["close"])

    df["bb_high_basis"] = bb_high["basis"]
    df["bb_high_lower"] = bb_high["lower"]

    df["bb_low_basis"] = bb_low["basis"]
    df["bb_low_lower"] = bb_low["lower"]

    df["bb_close_basis"] = bb_close["basis"]
    df["bb_close_lower"] = bb_close["lower"]

    return df


def bullish_break_condition(df: pd.DataFrame) -> bool:
    """Check Strategy 1 lower-band crossover condition on the last two candles."""
    if len(df) < BB_LENGTH + 2:
        return False
    prev = df.iloc[-2]
    curr = df.iloc[-1]

    cond_prev = (prev.bb_high_lower >= prev.bb_low_lower) and (prev.bb_high_lower >= prev.bb_close_lower)
    cond_now = (curr.bb_high_lower < curr.bb_low_lower) and (curr.bb_high_lower < curr.bb_close_lower)
    return cond_prev and cond_now


def price_above_all_bases(row: pd.Series) -> bool:
    return (
        (row.close > row.bb_high_basis)
        and (row.close > row.bb_low_basis)
        and (row.close > row.bb_close_basis)
    )


def strategy1_signal(df: pd.DataFrame) -> bool:
    """Determine if Strategy 1 buy signal is present on the latest candle."""
    if len(df) < BB_LENGTH + 2:
        return False
    if not bullish_break_condition(df):
        return False
    curr = df.iloc[-1]
    return price_above_all_bases(curr)


def lower_non_increasing(series: pd.Series, tolerance: int = 1) -> bool:
    """Return True if the series is mostly flat/declining (allowing limited upticks)."""
    diffs = series.diff()
    increases = (diffs > 0).sum()
    return increases <= tolerance


def strategy2_up_trend(df: pd.DataFrame) -> bool:
    """Check Strategy 2 continuation conditions on the latest N candles."""
    if len(df) < BB_LENGTH + N_TREND_CONTINUE:
        return False
    recent = df.iloc[-N_TREND_CONTINUE:]

    # Price remains above all middle bands for each candle
    price_condition = recent.apply(price_above_all_bases, axis=1).all()

    # Lower bands staying flat or drifting down (at most 1 uptick allowed)
    lower_ok = (
        lower_non_increasing(recent.bb_high_lower)
        and lower_non_increasing(recent.bb_low_lower)
        and lower_non_increasing(recent.bb_close_lower)
    )

    return price_condition and lower_ok


def strategy2_trend_end(df: pd.DataFrame) -> bool:
    """Check Strategy 2 termination conditions over the last M candles."""
    if len(df) < BB_LENGTH + M_TREND_END:
        return False
    recent = df.iloc[-M_TREND_END:]

    # Condition 1: price dips below any middle band within recent candles
    price_break = (
        (recent["close"] < recent[["bb_high_basis", "bb_low_basis", "bb_close_basis"]].min(axis=1))
    ).any()

    # Condition 2: at least two lower bands rising toward price consistently
    increases = {
        "bb_high_lower": (recent.bb_high_lower.diff() > 0).iloc[1:].all(),
        "bb_low_lower": (recent.bb_low_lower.diff() > 0).iloc[1:].all(),
        "bb_close_lower": (recent.bb_close_lower.diff() > 0).iloc[1:].all(),
    }
    rising_bands = sum(increases.values())
    reversing_lowers = rising_bands >= 2

    return price_break or reversing_lowers


def analyze_symbol(symbol: str) -> Dict[str, str]:
    """Fetch data for a symbol and evaluate strategies."""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=LOOKBACK_CANDLES)
    except Exception as exc:  # network or rate limit errors
        return {"symbol": symbol, "signal": "ERROR", "detail": str(exc)}

    if len(ohlcv) < BB_LENGTH + N_TREND_CONTINUE:
        return {"symbol": symbol, "signal": "INSUFFICIENT_DATA", "detail": ""}

    df = prepare_dataframe(ohlcv)
    # Drop initial rows without full Bollinger data
    df = df.dropna().reset_index(drop=True)

    if len(df) < N_TREND_CONTINUE:
        return {"symbol": symbol, "signal": "INSUFFICIENT_DATA", "detail": ""}

    last_close = df.iloc[-1].close
    signal = "NO_SIGNAL"
    detail = ""

    if strategy1_signal(df):
        signal = "STRATEGY1_BUY_SIGNAL"
        detail = "Bullish break with close above all bases"
    elif strategy2_trend_end(df):
        signal = "STRATEGY2_TREND_END"
        detail = "Price/bands suggest uptrend exhaustion"
    elif strategy2_up_trend(df):
        signal = "STRATEGY2_UP_TREND_CONTINUES"
        detail = "Price above bases; lower bands staying low"

    return {
        "symbol": symbol,
        "signal": signal,
        "close": f"{last_close:.6f}",
        "bb_high_basis": f"{df.iloc[-1].bb_high_basis:.6f}",
        "bb_low_basis": f"{df.iloc[-1].bb_low_basis:.6f}",
        "bb_close_basis": f"{df.iloc[-1].bb_close_basis:.6f}",
        "detail": detail,
    }


def scan_all_symbols():
    """Scan all USDT-M perpetual symbols and print findings."""
    symbols = fetch_usdtm_symbols()
    results = []
    for symbol in symbols:
        outcome = analyze_symbol(symbol)
        results.append(outcome)

    header = (
        f"{'SYMBOL':<12} | {'SIGNAL':<28} | {'CLOSE':<12} | "
        f"{'BB_HIGH_BASIS':<14} | {'BB_LOW_BASIS':<14} | {'BB_CLOSE_BASIS':<14} | DETAIL"
    )
    print("-" * len(header))
    print(header)
    print("-" * len(header))
    for res in results:
        print(
            f"{res['symbol']:<12} | {res['signal']:<28} | {res.get('close', ''):<12} | "
            f"{res.get('bb_high_basis', ''):<14} | {res.get('bb_low_basis', ''):<14} | "
            f"{res.get('bb_close_basis', ''):<14} | {res.get('detail', '')}"
        )
    print("-" * len(header))


if __name__ == "__main__":
    while True:
        try:
            scan_all_symbols()
        except Exception as exc:
            # Catch-all to keep the scanner running (e.g., network hiccups)
            print(f"[ERROR] {exc}")
        time.sleep(SLEEP_SECONDS)
