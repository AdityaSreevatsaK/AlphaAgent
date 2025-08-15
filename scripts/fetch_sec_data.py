import json

from src.data_ingestion.sec_downloader import download_filings
from src.utils import config, logger_config

logger = logger_config.logger


def main():
    """
    Main script to download 10-K and 8-K filings for target companies.
    """
    logger.info("Starting SEC filing download process...")

    # Load target companies to get the list of tickers
    with open(config.RAW_DATA_DIR / "target_companies.json", "r") as f:
        target_companies = json.load(f)
    target_tickers = [company["ticker"] for company in target_companies]

    # Load the full ticker-CIK map
    with open(config.RAW_DATA_DIR / "company_tickers.json", "r") as f:
        full_ticker_data = json.load(f)

    # Create the ticker-to-CIK mapping dictionary
    ticker_cik_map = {
        value["ticker"]: str(value["cik_str"])
        for key, value in full_ticker_data.items()
    }
    logger.info("Successfully loaded data and created CIK map.")

    # Call the reusable download function from the src module
    download_filings(ticker_cik_map, target_tickers)

    logger.info("SEC filing download process completed.")


if __name__ == "__main__":
    main()
