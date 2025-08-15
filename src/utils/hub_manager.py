import logging
from pathlib import Path

from huggingface_hub import snapshot_download

from src.utils import config

# Get the logger
logger = logging.getLogger(__name__)


def get_from_hub(repo_id: str, local_dir_name: str, repo_type: str = "dataset") -> Path:
    """
    Downloads a repository from the Hugging Face Hub if it doesn't exist locally.

    This function is cache-aware. It first checks if the target directory
    already exists. If it does, it returns the local path. If not, it
    downloads the repository from the Hub and returns the path.

    Args:
        repo_id (str): The ID of the repository on the Hugging Face Hub (e.g., "YourUsername/YourRepo").
        local_dir_name (str): The name of the folder within the project's data
                              directory to store the files (e.g., "filings", "vector_store").
        repo_type (str, optional): The type of the repository ('dataset', 'model', 'space').
                                   Defaults to "dataset".

    Returns:
        Path: The local path to the downloaded or existing data.
    """
    # Define the local path based on the project's data directory structure
    local_path = config.DATA_DIR / local_dir_name

    # Check if the data already exists locally
    if local_path.exists() and any(local_path.iterdir()):
        logger.info(f"Data found locally at '{local_path}'. Skipping download.")
        return local_path
    else:
        logger.info(
            f"Data not found locally. Downloading from Hugging Face Hub: {repo_id}"
        )
        # Ensure the parent directory exists
        local_path.mkdir(parents=True, exist_ok=True)

        # Download the entire repository snapshot from the Hub
        snapshot_download(
            repo_id=repo_id,
            repo_type=repo_type,
            local_dir=local_path,
            local_dir_use_symlinks=False,  # Set to False for Windows compatibility
        )
        logger.info(f"Successfully downloaded data to '{local_path}'.")
        return local_path
