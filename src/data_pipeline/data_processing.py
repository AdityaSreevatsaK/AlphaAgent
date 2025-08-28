import logging
import re

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def clean_sec_filing_text(html_content: str) -> str:
    """
    Cleans the HTML content of an SEC filing to extract plain text.

    Args:
        html_content (str): The raw HTML content of the filing.

    Returns:
        str: The cleaned, plain text content.
    """
    try:
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html_content, "lxml")

        # Extract the text
        text = soup.get_text(separator=" ")

        # --- Basic Text Normalization ---
        # Replace multiple spaces, newlines, and tabs with a single space
        text = re.sub(r"\s+", " ", text)

        # You could add more advanced logic here to remove boilerplate sections
        # For example, using regex to find and remove common disclaimer patterns.

        return text.strip()
    except Exception as e:
        logger.error(f"Error cleaning SEC filing: {e}", exc_info=True)
        return ""


def process_news_data(news_articles: list) -> str:
    """
    Processes a list of news articles from Finnhub into a single text block.

    Args:
        news_articles (list): A list of article dictionaries from the Finnhub JSON.

    Returns:
        str: A concatenated string of all headlines and summaries.
    """

    full_text = []
    for article in news_articles:
        headline = article.get("headline", "")
        summary = article.get("summary", "")

        # Combine headline and summary for each article
        if headline and summary:
            full_text.append(f"{headline.strip()}. {summary.strip()}")

    # Join all the processed articles into a single block of text
    return "\n\n".join(full_text)
