"""Offline regression checks for live-market data formatting; no requests leave CI."""
from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "tools" / "quantitative_tool.py"


def load_tool():
    finance = types.ModuleType("yfinance")
    finance.Ticker = Mock()
    logger_module = types.ModuleType("src.utils.logger_config")
    logger_module.logger = Mock()
    spec = importlib.util.spec_from_file_location("alpha_quantitative_under_test", SOURCE)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"yfinance": finance, "src.utils.logger_config": logger_module}):
        spec.loader.exec_module(module)
    return module


class QuantitativeToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_tool()

    def setUp(self):
        self.module.QuantitativeTool._get_ticker_info.cache_clear()
        self.module.yf.Ticker.reset_mock()
        self.module.yf.Ticker.side_effect = None
        self.module.yf.Ticker.return_value = Mock()

    def test_financial_ratios_format_with_live_fields(self):
        self.module.yf.Ticker.return_value.info = {
            "regularMarketPrice": 125,
            "trailingPE": 18.256,
            "priceToBook": 1.5,
            "dividendYield": 0.0125,
            "marketCap": 1_000_000,
        }
        result = self.module.QuantitativeTool().get_key_financial_ratios("EXAMPLE")
        self.assertIn("P/E Ratio (Trailing): 18.26", result)
        self.assertIn("P/B Ratio: 1.50", result)
        self.assertIn("Dividend Yield: 1.25%", result)
        self.assertIn("Market Cap: $1,000,000", result)
        self.module.yf.Ticker.assert_called_once_with("EXAMPLE")

    def test_missing_ticker_data_fails_closed(self):
        self.module.yf.Ticker.return_value.info = {}
        self.assertEqual(
            self.module.QuantitativeTool().get_key_financial_ratios("MISSING"),
            "Could not retrieve financial data for MISSING.",
        )

    def test_missing_ratios_do_not_raise(self):
        self.module.yf.Ticker.return_value.info = {"regularMarketPrice": 99}
        result = self.module.QuantitativeTool().get_key_financial_ratios("PARTIAL")
        self.assertIn("P/E Ratio (Trailing): N/A", result)
        self.assertIn("Dividend Yield: N/A", result)

    def test_fetch_exception_is_not_reported_as_market_data(self):
        self.module.yf.Ticker.side_effect = RuntimeError("offline")
        result = self.module.QuantitativeTool().get_key_financial_ratios("FAIL")
        self.assertIn("Could not retrieve financial data for FAIL.", result)

    def test_cached_info_does_not_repeat_network_call(self):
        self.module.yf.Ticker.return_value.info = {"regularMarketPrice": 3}
        tool = self.module.QuantitativeTool()
        tool.get_key_financial_ratios("CACHE")
        tool.get_key_financial_ratios("CACHE")
        self.module.yf.Ticker.assert_called_once_with("CACHE")

    def test_daily_performance_uses_latest_row(self):
        history = types.SimpleNamespace(
            empty=False,
            iloc=[{"Open": 100, "High": 110, "Low": 95, "Close": 105, "Volume": 5000}],
        )
        self.module.yf.Ticker.return_value.history.return_value = history
        text = self.module.QuantitativeTool.get_daily_stock_performance("DAILY")
        self.assertIn("Open: $100.00", text)
        self.assertIn("Close: $105.00", text)
        self.assertIn("Volume: 5,000", text)
        self.module.yf.Ticker.return_value.history.assert_called_once_with(period="1d")

    def test_daily_performance_handles_empty_and_api_failure(self):
        self.module.yf.Ticker.return_value.history.return_value = types.SimpleNamespace(empty=True)
        self.assertEqual(
            self.module.QuantitativeTool.get_daily_stock_performance("EMPTY"),
            "No daily performance data found for EMPTY.",
        )
        self.module.yf.Ticker.return_value.history.side_effect = ConnectionError("offline")
        self.assertIn(
            "An error occurred",
            self.module.QuantitativeTool.get_daily_stock_performance("OFFLINE"),
        )


if __name__ == "__main__":
    unittest.main()
