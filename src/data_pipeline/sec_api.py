import os

import requests
from dotenv import load_dotenv

from src.utils.logger_config import logger

# Load environment variables from .env file
load_dotenv()


def get_company_tickers():
    """
    Fetches the complete company ticker to CIK mapping from the SEC EDGAR API.
    """
    # Define your user agent and the headers
    headers = {"User-Agent": os.getenv("SEC_USER_AGENT")}

    url = "https://www.sec.gov/files/company_tickers.json"
    logger.info("Fetching data from SEC EDGAR...")
    response = requests.get(url, headers=headers)

    # Raise an exception for bad status codes (4xx or 5xx)
    response.raise_for_status()

    logger.info("Successfully fetched data.")
    return response.json()
