from pathlib import Path

import torch
from llama_index.core import (
    load_index_from_storage,
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.chat_engine import CondenseQuestionChatEngine
from llama_index.core.memory import ChatMemoryBuffer
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

    @staticmethod
    def run_pipeline(input_dir_path: str = None):
        """
        Runs the ingestion pipeline by loading documents from the 'news' and 'filings'
        subdirectories, generating their embeddings, and storing them in a vector index.

        Args:
            input_dir_path (str, optional): Path to the base directory containing
                'news' and 'filings' subdirectories. If not provided, uses the default
                processed data directory from config.
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


class RAGTool:
    """
    RAGTool encapsulates the retrieval and querying logic for the agent.

    This class loads a pre-built vector index from disk and provides a query
    method to interact with a chat engine, enabling conversational questioning
    of the indexed documents.

    Attributes:
        chat_engine (CondenseQuestionChatEngine): The chat engine used for querying.
    """

    def __init__(self):
        """
        Initialises the RAGTool by loading the index and setting up the chat engine.
        """
        self._load_index()
        self._setup_chat_engine()

    def _load_index(self):
        """
        Loads the FAISS vector index from the configured storage directory.
        """
        logger.info("Loading vector index from storage...")
        storage_context = StorageContext.from_defaults(
            persist_dir=str(config.VECTOR_STORE_DIR / "faiss_index")
        )
        self.index = load_index_from_storage(storage_context)
        logger.info("Vector index loaded successfully.")

    def _setup_chat_engine(self):
        """
        Sets up the chat engine with memory for conversational context.
        """
        logger.info("Setting up chat engine...")
        # Create a chat memory buffer to retain conversation history
        memory = ChatMemoryBuffer.from_defaults(token_limit=3900)

        self.chat_engine = CondenseQuestionChatEngine.from_defaults(
            query_engine=self.index.as_query_engine(),
            memory=memory,
        )
        logger.info("Chat engine setup complete.")

    def query(self, question: str) -> str:
        """
        Queries the chat engine with a given question and returns the response.

        Args:
            question (str): The user's question to be answered by the RAG pipeline.

        Returns:
            str: The response from the chat engine.
        """
        logger.info(f"Querying with question: '{question}'")
        response = self.chat_engine.chat(question)
        return str(response)
