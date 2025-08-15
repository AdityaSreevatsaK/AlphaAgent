import json

from dotenv import load_dotenv

from src.data_ingestion.fetch_news import fetch_company_news
from src.utils import config
from src.utils.logger_config import logger


def main():
    """
    Fetches and saves recent news for a predefined list of companies.

    This script serves as the main entry point for the news data ingestion
    process. It performs the following steps:
    1.  Loads necessary environment variables from a .env file (e.g., API keys
        for the news service).
    2.  Reads a list of target company tickers from a JSON file specified
        in the project configuration (`config.RAW_DATA_DIR / 'target_companies.json'`).
    3.  Invokes the `fetch_company_news` function to download and save the
        news data for each ticker.
    4.  Logs the progress and completion of the operation.

    This script is intended to be run directly from the command line and relies
    on a correctly configured `.env` file and `target_companies.json`.
    """
    # Load environment variables from .env file
    load_dotenv()

    logger.info("Starting news fetching process...")

    # Load target companies to get the list of tickers
    with open(config.RAW_DATA_DIR / "target_companies.json", "r") as f:
        target_companies = json.load(f)
    target_tickers = [company["ticker"] for company in target_companies]

    logger.info(f"Loaded {len(target_tickers)} target companies.")

    # Call the reusable news fetching function
    fetch_company_news(target_tickers)

    logger.info("News fetching process completed.")


if __name__ == "__main__":
    main()
