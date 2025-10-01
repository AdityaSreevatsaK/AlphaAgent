import math
from pathlib import Path

import torch
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from src.utils import config
from src.utils.logger_config import logger


class IngestionPipeline:
    """
    Orchestrating the process of loading documents, generating embeddings,
    and storing them in a vector index for efficient retrieval.

    Attributes:
        embedding_model_name (str): The name of the HuggingFace embedding model to use.
        device (str): The device to use for computation ('cuda' or 'cpu').
        batch_size (int): The number of embeddings to generate in a single batch.
    """

    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the IngestionPipeline with the specified embedding model.

        Args:
            embedding_model_name (str, optional): The name of the HuggingFace embedding model to use.
                                                    Defaults to "all-MiniLM-L6-v2".

        Attributes:
            embedding_model_name (str): The name of the embedding model.
        """
        self.embedding_model_name = embedding_model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.batch_size = 512 if self.device == "cuda" else 32
        self._setup_settings()

    def _setup_settings(self):
        """
        Configure global LlamaIndex settings for embeddings and node parsing.

        This method sets up the embedding model and node parser for LlamaIndex,
        selecting the appropriate device (GPU or CPU) and batch size for embedding
        generation. It logs the device in use, warns if falling back to CPU, and
        applies the configured embedding model and node parser to the global
        LlamaIndex `Settings`.

        Logs:
            - The device being used (CPU or CUDA).
            - A warning if GPU is not available.
            - The embedding batch size.
            - Confirmation of LlamaIndex settings configuration.
        """
        logger.info(f"Using device: {self.device}")
        if self.device == "cpu":
            logger.warning(
                "GPU not available, falling back to CPU. Ingestion will be slow."
            )

        # Initialise the embedding model with the specified device.
        embed_model = HuggingFaceEmbedding(
            model_name=self.embedding_model_name, device=self.device
        )
        embed_model.embed_batch_size = self.batch_size
        logger.info(f"Set embedding batch size to: {self.batch_size}")

        # Define how documents are split into nodes (chunks).
        node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)

        # Apply these settings globally for LlamaIndex.
        Settings.embed_model = embed_model
        Settings.node_parser = node_parser
        logger.info(
            f"LlamaIndex Settings configured with model: {self.embedding_model_name}"
        )

    def run_pipeline(self, input_dir_path: str = None):
        """
        Execute the full ingestion pipeline: load documents, parse them into nodes,
        generate embeddings, and persist the final vector index.

        Args:
            input_dir_path (str, optional): Path to the base directory containing processed data.
                If not provided, uses the default from config.PROCESSED_DATA_DIR.

        Returns:
            None

        Logs:
            - Start and completion of the ingestion pipeline.
            - Warnings if no documents are found.
            - Progress of document parsing and node creation.
            - Estimated embedding workload and time.
            - Success message with the path to the saved vector index.
        """
        logger.info("Starting ingestion pipeline...")

        # Determine the base directory for processed data.
        base_processed_dir = (
            Path(input_dir_path) if input_dir_path else config.PROCESSED_DATA_DIR
        )

        # Load the documents from their respective subdirectories.
        all_documents = self._load_documents(base_processed_dir)
        if not all_documents:
            return  # Stop if no documents were found.

        # First parse the documents into nodes to get a count.
        logger.info("Parsing documents into nodes...")
        nodes = Settings.node_parser.get_nodes_from_documents(
            all_documents, show_progress=True
        )

        # Log the estimates before starting the heavy computation.
        self._log_embedding_estimates(len(nodes))

        logger.info("Creating vector store index. This may take some time...")
        # Create the index from the pre-parsed nodes.
        index = VectorStoreIndex(nodes, show_progress=True)

        # Define the path for the persistent index and save it.
        index_path = str(config.VECTOR_STORE_DIR / "faiss_index")
        index.storage_context.persist(persist_dir=index_path)
        logger.info(f"Successfully created and saved the vector index to: {index_path}")

    @staticmethod
    def _load_documents(self, base_dir: Path) -> list:
        """
        Load documents from the specified base directory.

        This function attempts to load documents from two subdirectories within
        the given base directory: 'news' and 'filings'. It uses the
        SimpleDirectoryReader to read documents from each subdirectory (non-recursive
        for 'news', recursive for 'filings'). Loaded documents are aggregated into a
        single list.

        Args:
            base_dir (Path): The base directory containing 'news' and 'filings' subdirectories.

        Returns:
            list: A list of loaded document objects. If no documents are found, returns an empty list.

        Logs:
            - Info messages for successful loads and total document count.
            - Warnings if a subdirectory is missing.
            - Error if no documents are found in either subdirectory.
        """
        all_documents = []
        news_path = base_dir / "news"
        filings_path = base_dir / "filings"

        if news_path.exists():
            logger.info(f"Loading documents from: {news_path}")
            news_reader = SimpleDirectoryReader(str(news_path), recursive=False)
            news_docs = news_reader.load_data()
            all_documents.extend(news_docs)
            logger.info(f"Loaded {len(news_docs)} news documents.")
        else:
            logger.warning(f"News directory not found at '{news_path}'. Skipping.")

        if filings_path.exists():
            logger.info(f"Loading documents from: {filings_path}")
            filings_reader = SimpleDirectoryReader(str(filings_path), recursive=True)
            filings_docs = filings_reader.load_data()
            all_documents.extend(filings_docs)
            logger.info(f"Loaded {len(filings_docs)} filing documents.")
        else:
            logger.warning(
                f"Filings directory not found at '{filings_path}'. Skipping."
            )

        if not all_documents:
            logger.error(
                f"No documents found in subdirectories of '{base_dir}'. Aborting."
            )
        else:
            logger.info(f"Loaded a total of {len(all_documents)} documents.")

        return all_documents

    def _log_embedding_estimates(self, total_nodes: int):
        """
        Log estimated embedding workload and time for the ingestion process.

        Args:
            total_nodes (int): The total number of nodes (embeddings) to generate.

        Logs:
            - Total embeddings to generate.
            - Number of embedding iterations (batches).
        """
        if total_nodes == 0:
            return

        # Calculate the number of batches required.
        iterations = math.ceil(total_nodes / self.batch_size)

        logger.info(f"Total embeddings to generate: {total_nodes}")
        logger.info(f"Number of embedding iterations (batches): {iterations}")
