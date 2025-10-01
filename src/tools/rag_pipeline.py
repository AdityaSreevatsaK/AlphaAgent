from pathlib import Path

import torch
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from src.utils import config
from src.utils.logger_config import logger


class IngestionPipeline:
    """
    IngestionPipeline orchestrates the process of loading documents, generating embeddings,
    and storing them in a vector index for efficient retrieval.

    Attributes:
        embedding_model_name (str): Name of the HuggingFace embedding model to use.
    """

    def __init__(self, embedding_model_name: str = "BAAI/bge-large-en-v1.5"):
        """
        Initialises the IngestionPipeline.
        """
        self.embedding_model_name = embedding_model_name
        self._setup_settings()

    def _setup_settings(self):
        """
        Configures LlamaIndex settings, detects GPU, and sets device
        and batch size accordingly.
        """
        # --- GPU Check and Device Configuration ---
        device = "cuda" if torch.cuda.is_available() else "cpu"
        batch_size = (
            128 if device == "cuda" else 16
        )  # Larger batch for GPU, smaller for CPU

        logger.info(f"Using device: {device}")
        if device == "cpu":
            logger.warning(
                "GPU not available, falling back to CPU. Ingestion will be slow."
            )

        # --- Configure Embedding Model ---
        embed_model = HuggingFaceEmbedding(
            model_name=self.embedding_model_name, device=device
        )
        embed_model.embed_batch_size = batch_size
        logger.info(f"Set embedding batch size to: {batch_size}")

        # --- Configure Node Parser (SentenceSplitter) ---
        node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)

        # --- Set Global Settings ---
        Settings.embed_model = embed_model
        Settings.node_parser = node_parser
        logger.info(
            f"LlamaIndex Settings configured with model: {self.embedding_model_name}"
        )

    def run_pipeline(self, input_dir_path: str = None):
        """
        Executes the full ingestion pipeline by explicitly loading from
        the 'news' and 'filings' subdirectories.
        """
        logger.info("Starting ingestion pipeline...")

        base_processed_dir = (
            Path(input_dir_path) if input_dir_path else config.PROCESSED_DATA_DIR
        )

        news_path = base_processed_dir / "news"
        filings_path = base_processed_dir / "filings"
        all_documents = []

        # 1. Load documents from the 'news' directory (non-recursively).
        if news_path.exists():
            logger.info(f"Loading documents from: {news_path}")
            news_reader = SimpleDirectoryReader(
                input_dir=str(news_path), recursive=False
            )
            news_docs = news_reader.load_data()
            all_documents.extend(news_docs)
            logger.info(f"Loaded {len(news_docs)} news documents.")
        else:
            logger.warning(f"News directory not found at '{news_path}'. Skipping.")

        # 2. Load documents from the 'filings' directory (recursively).
        if filings_path.exists():
            logger.info(f"Loading documents from: {filings_path}")
            filings_reader = SimpleDirectoryReader(
                input_dir=str(filings_path), recursive=True
            )
            filings_docs = filings_reader.load_data()
            all_documents.extend(filings_docs)
            logger.info(f"Loaded {len(filings_docs)} filing documents.")
        else:
            logger.warning(
                f"Filings directory not found at '{filings_path}'. Skipping."
            )

        if not all_documents:
            logger.error(
                f"No documents found in subdirectories of '{base_processed_dir}'. Aborting."
            )
            return

        logger.info(f"Loaded a total of {len(all_documents)} documents.")

        logger.info("Creating vector store index. This may take some time...")
        index = VectorStoreIndex.from_documents(all_documents, show_progress=True)

        index_path = str(config.VECTOR_STORE_DIR / "faiss_index")
        index.storage_context.persist(persist_dir=index_path)

        logger.info(f"Successfully created and saved the vector index to: {index_path}")
