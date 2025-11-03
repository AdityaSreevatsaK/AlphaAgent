import json
import logging
import os
from datetime import datetime, timedelta

import finnhub

from src.utils import config

# Get the logger
logger = logging.getLogger(__name__)


def fetch_company_news(target_tickers: list):
    """
    Fetches recent news articles for a list of company tickers using the Finnhub API.

    Args:
        target_tickers (list): A list of stock tickers to fetch news for.
    """
    # Load the Finnhub API key from environment variables
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        logger.error(
            "Finnhub API key not found. Please add FINNHUB_API_KEY to your .env file."
        )
        return

    # Setup Finnhub client
    finnhub_client = finnhub.Client(api_key=api_key)
    logger.info("Finnhub client initialized.")

    # Get news lookback days from config.yml
    news_api_config = config.get_config("news_api")
    news_lookback_days = news_api_config.get("lookback_days", 90)

    # Define the date range for the news (e.g., the last 90 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=news_lookback_days)
    date_format = "%Y-%m-%d"

    # Create a directory to save the news data
    news_dir = config.RAW_DATA_DIR / "news"
    news_dir.mkdir(exist_ok=True)

    for ticker in target_tickers:
        # Define the expected output path for the news file
        output_path = news_dir / f"{ticker}_news.json"

        # --- CACHING LOGIC START ---
        # Check if the file already exists before making an API call
        if output_path.exists():
            logger.info(f"News for {ticker} already exists. Skipping download.")
            continue  # Move to the next ticker
        # --- CACHING LOGIC END ---

        try:
            logger.info(f"Fetching news for {ticker}...")

            # Make the API call to Finnhub
            company_news = finnhub_client.company_news(
                ticker,
                _from=start_date.strftime(date_format),
                to=end_date.strftime(date_format),
            )

            # Save the news to a JSON file
            with open(output_path, "w") as f:
                json.dump(company_news, f, indent=4)

            logger.info(f"Successfully saved news for {ticker}.")

        except Exception as e:
            logger.error(f"Could not fetch news for {ticker}: {e}", exc_info=True)
