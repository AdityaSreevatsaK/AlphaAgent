import sys
from pathlib import Path

from src.tools.rag_pipeline import IngestionPipeline
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
    logger.info("Starting the RAG data ingestion process...")
    try:
        pipeline = IngestionPipeline()
        pipeline.run_pipeline()
        logger.info("RAG data ingestion process completed successfully.")
    except Exception as e:
        logger.error(
            f"An error occurred during the ingestion process: {e}", exc_info=True
        )


if __name__ == "__main__":
    main()
