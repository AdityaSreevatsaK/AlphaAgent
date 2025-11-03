import json
import os

import yfinance as yf

from src.utils.config import RAW_DATA_DIR


def fetch_and_save_company_data():
    """
    Fetches company details (name, sector) for a predefined list
    of tickers using the yfinance library.

    Saves the resulting data to 'target_companies.json'.
    """

    # This is the static input: the list of tickers to target.
    target_tickers = [
        "AAPL",
        "MSFT",
        "JPM",
        "TSLA",
        "AMZN",
        "NVDA",
        "BRK-B",
        "SONY",
        "TM",
        "INFY",
    ]

    companies_data = []
    output_filename = "target_companies.json"

    print(f"Starting data fetch for {len(target_tickers)} tickers...")

    for ticker_symbol in target_tickers:
        try:
            # Create a Ticker object
            ticker = yf.Ticker(ticker_symbol)

            # Fetch the company's info dictionary
            info = ticker.info

            # Extract the required data.
            # 'longName' is typically the full company name.
            # 'sector' provides the industry sector.
            company_name = info.get("longName")
            sector = info.get("sector")

            # Basic validation to ensure the essential data was found
            if not company_name or not sector:
                print(
                    f"Warning: Missing 'longName' or 'sector' for {ticker_symbol}. Skipping."
                )
                continue

            # Append the structured data to the list
            companies_data.append(
                {
                    "company_name": company_name,
                    "ticker": ticker_symbol,
                    "sector": sector,
                }
            )

            print(f"Successfully fetched data for: {ticker_symbol}")

        except Exception as e:
            # Handle potential errors (e.g., network issues, invalid ticker)
            print(f"Error fetching data for {ticker_symbol}: {e}")

    # After the loop, write the collected data to the JSON file
    try:
        with open(
            os.path.join(RAW_DATA_DIR, output_filename), "w", encoding="utf-8"
        ) as file:
            json.dump(companies_data, file, indent=4)

        print(f"\nFile generation complete: '{output_filename}' created successfully.")
        print(f"Total companies saved: {len(companies_data)}/{len(target_tickers)}")

    except IOError as e:
        print(f"Error: Failed to write to file '{output_filename}'. Details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during file writing: {e}")


if __name__ == "__main__":
    # Executes the data fetching and file creation process.
    fetch_and_save_company_data()
