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
