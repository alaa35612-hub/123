import unittest

from pre_pump_engine import EngineConfig, MarketBar, evaluate_pre_pump


def make_bar(i: int, **overrides):
    base = {
        "timestamp_ms": i * 60_000,
        "high": 100.2,
        "low": 99.8,
        "close": 100.0,
        "volume": 1200.0,
        "market_buy_volume": 700.0,
        "market_sell_volume": 500.0,
        "open_interest": 1_000_000.0 + i * 200.0,
        "funding_rate": -0.0001,
        "bid_depth_top": 200_000.0,
        "ask_depth_top": 200_000.0,
        "spot_volume": 10_000_000.0 + i * 5_000.0,
        "futures_volume": 12_000_000.0 + i * 8_000.0,
        "liquidation_cluster_density": 0.55,
        "whale_flow_score_raw": 0.45,
    }
    base.update(overrides)
    return MarketBar(**base)


class PrePumpEngineTests(unittest.TestCase):
    def test_high_probability_short_squeeze_setup(self):
        bars = [make_bar(i) for i in range(120)]

        # engineer 5-bar compression + OI spike + negative funding + thin depth
        for j in range(5):
            idx = 115 + j
            bars[idx] = make_bar(
                idx,
                high=100.1,
                low=99.95,
                close=100.0 + j * 0.01,
                open_interest=1_000_000 + (j * 20_000),
                funding_rate=-0.0025,
                market_buy_volume=950,
                market_sell_volume=350,
                bid_depth_top=70_000,
                ask_depth_top=70_000,
                liquidation_cluster_density=0.9,
                whale_flow_score_raw=0.85,
            )

        cfg = EngineConfig(
            funding_window_bars=60,
            atr_slow_bars=60,
        )
        result = evaluate_pre_pump(bars, cfg)

        self.assertGreaterEqual(result.pps, cfg.pps_watch_threshold)
        self.assertIn(result.decision_tree_state, {"HIGH_SHORT_SQUEEZE_PROBABILITY", "MONITOR"})

    def test_no_signal_on_flat_conditions(self):
        bars = [make_bar(i, market_buy_volume=600, market_sell_volume=600, funding_rate=0.0) for i in range(120)]
        cfg = EngineConfig(funding_window_bars=60, atr_slow_bars=60)
        result = evaluate_pre_pump(bars, cfg)

        self.assertLess(result.pps, 0.75)
        self.assertIn(result.regime, {"NO_SIGNAL", "WATCHLIST"})


if __name__ == "__main__":
    unittest.main()
