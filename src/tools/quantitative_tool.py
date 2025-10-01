from functools import lru_cache

import yfinance as yf

from src.utils.logger_config import logger


class QuantitativeTool:
    """
    A tool for fetching and analysing quantitative financial data using the yfinance library.

    This class provides methods to get key financial ratios, historical stock performance,
    and other essential metrics for a given stock ticker. It uses caching to avoid
    redundant API calls for the same ticker information.
    """

    @staticmethod
    @lru_cache(maxsize=100)  # Caches the results of this function
    def _get_ticker_info(ticker: str) -> dict:
        """
        Private helper method to fetch and cache the .info dictionary for a ticker.
        Using a cache prevents making repeated API calls for the same ticker in a short period.

        Args:
            ticker (str): The stock ticker symbol (e.g., "AAPL").

        Returns:
            dict: A dictionary containing comprehensive information about the ticker.
                  Returns an empty dictionary if the ticker is invalid or data is not found.
        """
        try:
            logger.info(f"Fetching financial data for {ticker}...")
            stock = yf.Ticker(ticker)
            info = stock.info
            if not info or info.get("regularMarketPrice") is None:
                logger.warning(
                    f"No data found for ticker: {ticker}. It might be de-listed or invalid."
                )
                return {}
            logger.info(f"Successfully fetched data for {ticker}.")
            return info
        except Exception as e:
            logger.error(f"An error occurred while fetching data for {ticker}: {e}")
            return {}

    def get_key_financial_ratios(self, ticker: str) -> str:
        """
        Provides key financial ratios for a given stock ticker.

        This tool fetches essential metrics like the P/E ratio, P/B ratio, and dividend yield,
        which are fundamental for assessing a company's valuation and financial health.

        Args:
            ticker (str): The stock ticker symbol (e.g., "AAPL").

        Returns:
            str: A formatted string containing the key financial ratios.
        """
        info = self._get_ticker_info(ticker)
        if not info:
            return f"Could not retrieve financial data for {ticker}."

        # Safely get each metric using .get() to avoid errors if a key is missing
        pe_ratio = info.get("trailingPE", "N/A")
        pb_ratio = info.get("priceToBook", "N/A")
        dividend_yield = info.get("dividendYield")
        market_cap = info.get("marketCap", 0)

        # Format the output nicely
        formatted_ratios = [
            f"Key Financial Ratios for {ticker}:",
            f"  - P/E Ratio (Trailing): {pe_ratio:.2f}"
            if isinstance(pe_ratio, (int, float))
            else f"  - P/E Ratio (Trailing): {pe_ratio}",
            f"  - P/B Ratio: {pb_ratio:.2f}"
            if isinstance(pb_ratio, (int, float))
            else f"  - P/B Ratio: {pb_ratio}",
            f"  - Dividend Yield: {dividend_yield * 100:.2f}%"
            if isinstance(dividend_yield, (int, float))
            else "  - Dividend Yield: N/A",
            f"  - Market Cap: ${market_cap:,}",
        ]
        return "\n".join(formatted_ratios)

    @staticmethod
    def get_daily_stock_performance(ticker: str) -> str:
        """
        Provides the daily stock performance for a given ticker.

        This tool fetches the open, high, low, and closing price, along with the trading
        volume for the most recent trading day. It's useful for assessing recent market activity.

        Args:
            ticker (str): The stock ticker symbol (e.g., "AAPL").

        Returns:
            str: A formatted string detailing the most recent daily stock performance.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if hist.empty:
                return f"No daily performance data found for {ticker}."

            latest_data = hist.iloc[-1]
            performance_details = [
                f"Most Recent Daily Stock Performance for {ticker}:",
                f"  - Open: ${latest_data['Open']:.2f}",
                f"  - High: ${latest_data['High']:.2f}",
                f"  - Low: ${latest_data['Low']:.2f}",
                f"  - Close: ${latest_data['Close']:.2f}",
                f"  - Volume: {latest_data['Volume']:,}",
            ]
            return "\n".join(performance_details)
        except Exception as e:
            logger.error(f"Failed to get daily performance for {ticker}: {e}")
            return f"An error occurred while fetching daily performance for {ticker}."
