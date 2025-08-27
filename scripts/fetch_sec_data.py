import json

from src.data_pipeline.sec_downloader import download_filings
from src.utils import config, logger_config

logger = logger_config.logger


def main():
    """
    Orchestrates the download of SEC filings for a predefined list of target companies.

    This script performs the following steps:
    1.  Loads the list of target company tickers from
        `data/raw/target_companies.json`.
    2.  Loads a comprehensive mapping of all company tickers to their CIK numbers
        from `data/raw/company_tickers.json`.
    3.  Constructs a dictionary that maps each target ticker to its corresponding CIK.
    4.  Calls the `download_filings` function to fetch and save the 10-K and 8-K
        filings for the target companies.

    The script assumes that `target_companies.json` and `company_tickers.json`
    exist in the `data/raw` directory.
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
