import json

from src.data_ingestion.sec_api import get_company_tickers
from src.utils import config
from src.utils.logger_config import logger


def main():
    """
    A runnable script that fetches company tickers and saves them to a file.
    """
    logger.info("Ticker fetching script started.")
    try:
        data = get_company_tickers()
        # Define where to save the raw data
        output_path = config.RAW_DATA_DIR / "company_tickers.json"

        logger.info(f"Saving data to {output_path}...")
        with open(output_path, "w") as f:
            json.dump(data, f, indent=4)
        logger.info("Data saved successfully.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")


# This makes the script runnable from the command line
if __name__ == "__main__":
    main()
