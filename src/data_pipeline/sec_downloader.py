from sec_edgar_downloader import Downloader

from src.utils import config, logger_config

logger = logger_config.logger


def download_filings(ticker_cik_map: dict, target_tickers: list):
    """
    Downloads 10-K and 8-K filings for a given list of tickers.

    Args:
        ticker_cik_map (dict): A dictionary mapping ticker symbols to CIKs.
        target_tickers (list): A list of ticker symbols to download filings for.
    """
    # Initialise the downloader with your user agent and download path
    dl = Downloader(
        company_name="AlphaAgent",
        email_address=config.SEC_USER_AGENT.split(" ")[
            -1
        ],  # Extract email from user agent
        download_folder=config.RAW_DATA_DIR / "filings",
    )

    for ticker in target_tickers:
        cik = ticker_cik_map.get(ticker)
        if not cik:
            logger.warning(f"CIK not found for ticker: {ticker}. Skipping.")
            continue

        try:
            logger.info(f"Fetching filings for {ticker} (CIK: {cik})...")
            # Get the 5 most recent 10-K filings
            dl.get(form="10-K", ticker_or_cik=cik, limit=5)
            # Get the 5 most recent 8-K filings
            dl.get(form="8-K", ticker_or_cik=cik, limit=5)
            logger.info(f"Successfully downloaded filings for {ticker}.")
        except Exception as e:
            logger.error(f"Could not download filings for {ticker}: {e}", exc_info=True)
