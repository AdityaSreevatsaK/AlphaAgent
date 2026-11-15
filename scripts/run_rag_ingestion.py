import argparse
import logging
import sys
from pathlib import Path

# Make direct script invocation work outside the repository root.
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.tools.rag_pipeline import IngestionPipeline
from src.utils import config
from src.utils.logger_config import logger


def main():
    """
    Main function to run the data ingestion pipeline.
    This script initialises and runs the IngestionPipeline, which processes
    documents from a specified directory and creates a searchable vector index.
    It now accepts a command-line argument for the input directory.
    """
    # --- Set Up Argument Parser ---
    # I've added an argument parser to make the script more flexible.
    # This allows you to specify the input directory from the command line.
    parser = argparse.ArgumentParser(description="Run the RAG data ingestion pipeline.")
    parser.add_argument(
        "--input-dir",
        type=str,
        default=str(config.PROCESSED_DATA_DIR),
        help="Path to the directory containing the processed data.",
    )
    args = parser.parse_args()

    # --- Silence Noisy Library Loggers ---
    for noisy in [
        "llama_index.core.node_parser.node_utils",
        "sentence_transformers",
        "filelock",
        "urllib3.connectionpool",
        "httpx",
    ]:
        logging.getLogger(noisy).setLevel(logging.WARNING)

    try:
        data_path = args.input_dir
        logger.info(f"Starting RAG data ingestion process from: {data_path}")

        pipeline = IngestionPipeline()
        pipeline.run_pipeline(input_dir_path=data_path)

        logger.info("RAG data ingestion process completed successfully.")
        return 0

    except Exception as e:
        logger.error(
            f"An error occurred during the ingestion process: {e}", exc_info=True
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
