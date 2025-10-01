import logging
import sys
from pathlib import Path

from src.tools.rag_pipeline import IngestionPipeline
from src.utils import config
from src.utils.logger_config import logger

# Add the project root to the Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))


def main():
    """
    Main function to run the data ingestion pipeline.
    This script initialises and runs the IngestionPipeline, which processes
    documents and creates a searchable vector index.
    """
    # --- Silence Noisy Library Loggers ---
    # I've set the log level to WARNING for libraries that are known to be
    # overly verbose during the ingestion process.
    logging.getLogger("llama_index.core.node_parser.node_utils").setLevel(
        logging.WARNING
    )
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("filelock").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    try:
        data_path = config.PROCESSED_DATA_DIR
        logger.info(f"Starting RAG data ingestion process from: {data_path}")

        pipeline = IngestionPipeline()
        pipeline.run_pipeline(input_dir_path=data_path)

        logger.info("RAG data ingestion process completed successfully.")
    except Exception as e:
        logger.error(
            f"An error occurred during the ingestion process: {e}", exc_info=True
        )


if __name__ == "__main__":
    main()
