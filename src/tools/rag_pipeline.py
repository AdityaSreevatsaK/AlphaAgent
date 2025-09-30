import torch
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from src.utils import config
from src.utils.logger_config import logger


class IngestionPipeline:
    """
    A pipeline for ingesting documents, creating embeddings, and storing them
    in a FAISS vector index.

    This class is responsible for the one-time, offline process of preparing
    the data that the RAG tool will query in real time.
    """

    def __init__(self, embedding_model_name: str = "BAAI/bge-large-en-v1.5"):
        """
        Initialises the IngestionPipeline.

        Args:
            embedding_model_name (str): The name of the Hugging Face model to use for embeddings.
        """
        self.embedding_model_name = embedding_model_name
        self._setup_settings()

    def _setup_settings(self):
        """Configures the global LlamaIndex settings and ensures GPU is used."""

        # --- Explicitly setting the device to CUDA, if available ---
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        if device == "cpu":
            logger.warning(
                "GPU not available, falling back to CPU. This will be very slow."
            )

        # Define the embedding model and explicitly set it to use the GPU
        embed_model = HuggingFaceEmbedding(
            model_name=self.embedding_model_name, device=device
        )

        # Configure the sentence splitter
        node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)

        # Set the global settings
        Settings.embed_model = embed_model
        Settings.node_parser = node_parser
        logger.info(
            f"LlamaIndex Settings configured with embedding model: {self.embedding_model_name}"
        )

    def run_pipeline(self, input_dir_path: str = None):
        """
        Executes the full ingestion pipeline.

        1.  Loads text documents from the processed data directory.
        2.  Chunks the documents into nodes using the SentenceSplitter.
        3.  Generates embeddings for each node.
        4.  Creates a FAISS vector index from the embeddings.
        5.  Saves the index to disk for later use by the RAGTool.
        """
        logger.info("Starting ingestion pipeline...")

        # Use the provided path, or default to the one from config
        if input_dir_path is None:
            input_dir_path = config.PROCESSED_DATA_DIR

        # 1. Load documents recursively
        logger.info(f"Recursively loading documents from: {input_dir_path}")
        reader = SimpleDirectoryReader(
            input_dir=str(input_dir_path),
            recursive=True,  # <-- This is the crucial change
        )
        documents = reader.load_data()

        if not documents:
            logger.error(f"No documents found in '{input_dir_path}'. Aborting.")
            return

        logger.info(f"Loaded {len(documents)} documents.")

        # 2 & 3. Create VectorStoreIndex (handles chunking and embedding automatically)
        logger.info("Creating vector store index. This may take some time...")
        index = VectorStoreIndex.from_documents(documents, show_progress=True)

        # 4 & 5. Persist the index to disk
        index_path = str(config.VECTOR_STORE_DIR / "faiss_index")
        index.storage_context.persist(persist_dir=index_path)

        logger.info(f"Successfully created and saved the vector index to: {index_path}")
