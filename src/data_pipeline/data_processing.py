import logging
import re

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def clean_sec_filing_text(raw_filing_text: str) -> str:
    """
    Cleans the raw text of a full SEC filing submission.
    It finds the primary document text (like a 10-K) within the raw file,
    parses its HTML, and extracts clean, readable text.
    """
    try:
        # Regex to find the start of the first document, which is usually the main report
        doc_start_match = re.search(r"<DOCUMENT>", raw_filing_text)
        doc_end_match = re.search(r"</DOCUMENT>", raw_filing_text)

        if not doc_start_match or not doc_end_match:
            logger.warning("Could not find <DOCUMENT> tags in the filing.")
            return ""

        # Extract the content between the first <DOCUMENT> and </DOCUMENT> tags
        document_text = raw_filing_text[doc_start_match.end() : doc_end_match.start()]

        # Now, parse the extracted document text with BeautifulSoup
        soup = BeautifulSoup(document_text, "lxml")

        # Get text and normalize whitespace
        text = soup.get_text(separator=" ")
        cleaned_text = re.sub(r"\s+", " ", text).strip()

        return cleaned_text
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
