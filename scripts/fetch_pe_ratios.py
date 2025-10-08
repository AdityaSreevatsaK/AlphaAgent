from datetime import datetime, timezone

import yfinance as yf

from ..src.utils.logger_config import setup_logging


def fetch_pe(ticker="MSFT"):
    """
    Fetches and logs P/E ratios and related financial data for a given stock ticker using yfinance.

    Args:
        ticker (str): The stock ticker symbol to fetch data for. Defaults to "MSFT" (Microsoft).

    Logs:
        - Ticker symbol
        - Market time in UTC and exchange timezone
        - Current price
        - Trailing P/E ratio
        - Forward P/E ratio
        - Trailing EPS
        - Sanity check: price / trailing EPS compared to trailing P/E

    Returns:
        None
    """
    log = setup_logging()
    t = yf.Ticker(ticker)
    info = (
        t.get_info()
    )  # returns dict with trailingPE/forwardPE/regularMarketPrice/etc.

    price = info.get("regularMarketPrice") or info.get("currentPrice")
    trailing_pe = info.get("trailingPE")
    forward_pe = info.get("forwardPE")
    trailing_eps = info.get("trailingEps")
    ts = info.get("regularMarketTime")
    tz = info.get("exchangeTimezoneName") or "UTC"

    log.info(f"Ticker: {ticker}")
    if ts:
        log.info(
            f"marketTime_utc: {datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()} | exchange_tz: {tz}"
        )
    log.info(f"price: {price}")
    log.info(f"trailingPE: {trailing_pe}")
    log.info(f"forwardPE: {forward_pe}")
    log.info(f"trailingEps: {trailing_eps}")

    # Quick sanity check: price / trailingEps ≈ trailingPE
    if price and trailing_eps:
        try:
            approx = price / trailing_eps
            log.info(
                f"price/trailingEps: {approx:.2f}  (diff from trailingPE: "
                f"{None if trailing_pe is None else round(approx - trailing_pe, 2)})"
            )
        except Exception as e:
            log.info(f"Check failed: {e}")


if __name__ == "__main__":
    fetch_pe()
