import json

from src.data_pipeline.data_processing import clean_sec_filing_text, process_news_data
from src.utils import config
from src.utils.logger_config import logger


def main():
    """
    Processes raw SEC filings and news data, cleaning and transforming them
    into plain text files ready for analysis.

    The script performs two main tasks:

    1.  **SEC Filing Processing:**
        -   Searches for raw HTML filings (`full-submission.txt`) within the
          `data/raw/filings/sec-edgar-filings` directory.
        -   Cleans each filing by removing HTML tags and normalizing whitespace
          using the `clean_sec_filing_text` function.
        -   Saves the cleaned text to `data/processed/filings`, mirroring the
          original directory structure.

    2.  **News Data Processing:**
        -   Finds all company-specific news `*.json` files in `data/raw/news`.
        -   Consolidates headlines and summaries from each file into a single
          text block using the `process_news_data` function.
        -   Saves the result as a `.txt` file in `data/processed/news`.

    If a source directory is not found, the script logs a warning and skips
    that processing step, allowing for a partial run.
    """
    logger.info("Starting raw data processing...")

    # --- 1. Process SEC Filings ---
    raw_filings_dir = config.RAW_DATA_DIR / "filings" / "sec-edgar-filings"
    processed_filings_dir = config.PROCESSED_DATA_DIR / "filings"
    processed_filings_dir.mkdir(parents=True, exist_ok=True)

    if not raw_filings_dir.exists():
        logger.warning(
            f"Raw filings directory not found at {raw_filings_dir}. Skipping SEC processing."
        )
    else:
        # Find all the raw filing text files
        filing_files = list(raw_filings_dir.rglob("full-submission.txt"))
        logger.info(f"Found {len(filing_files)} SEC filings to process.")

        for file_path in filing_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    html_content = f.read()

                cleaned_text = clean_sec_filing_text(html_content)

                # Create a corresponding path in the processed directory
                relative_path = file_path.relative_to(raw_filings_dir)
                output_path = processed_filings_dir / relative_path.with_suffix(".txt")
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(cleaned_text)

            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {e}")

    # --- 2. Process News Data ---
    raw_news_dir = config.RAW_DATA_DIR / "news"
    processed_news_dir = config.PROCESSED_DATA_DIR / "news"
    processed_news_dir.mkdir(parents=True, exist_ok=True)

    if not raw_news_dir.exists():
        logger.warning(
            f"Raw news directory not found at {raw_news_dir}. Skipping news processing."
        )
    else:
        news_files = list(raw_news_dir.glob("*.json"))
        logger.info(f"Found {len(news_files)} news files to process.")

        for file_path in news_files:
            try:
                with open(file_path, "r") as f:
                    articles = json.load(f)

                processed_text = process_news_data(articles)

                # Save the combined text for each company
                output_path = processed_news_dir / file_path.with_suffix(".txt").name

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(processed_text)

            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {e}")

    logger.info("Raw data processing complete.")


if __name__ == "__main__":
    main()
