import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import HfApi, list_repo_files
from huggingface_hub import login
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


def upload_to_hub(
    repo_id: str, local_dir_name: str, path_in_repo: str, repo_type: str = "dataset"
):
    """
    Uploads a local directory to the Hugging Face Hub.

    Args:
        repo_id (str): The ID of the repository on the Hub.
        local_dir_name (str): The name of the local folder within the project's data directory.
        path_in_repo (str): The target subfolder path within the Hub repository.
        repo_type (str, optional): The type of the repository. Defaults to "dataset".
    """
    logger.info(
        f"Starting upload of '{local_dir_name}' to Hugging Face Hub repo '{repo_id}'..."
    )

    load_dotenv()
    hf_token = os.getenv("HUGGINGFACE_ALPHA_AGENT_DATA_REPO_KEY")
    if not hf_token:
        logger.error(
            "Hugging Face token not found. Please add HF_TOKEN to your .env file."
        )
        return

    login(token=hf_token)
    logger.info("Successfully logged in to Hugging Face Hub.")

    api = HfApi()
    local_path = config.DATA_DIR / local_dir_name

    if not local_path.exists():
        logger.error(f"Local directory not found at '{local_path}'. Aborting upload.")
        return

    try:
        logger.info(
            f"Uploading directory '{local_path}' to '{path_in_repo}' in the repo..."
        )
        api.upload_folder(
            folder_path=str(local_path),
            repo_id=repo_id,
            repo_type=repo_type,
            path_in_repo=path_in_repo,
        )
        logger.info("Upload completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during upload: {e}", exc_info=True)


def check_hub_path_exists(
    repo_id: str, path_in_repo: str, repo_type: str = "dataset"
) -> bool:
    """
    Checks if a specific path (file or folder) exists in a Hugging Face Hub repository.

    Args:
        repo_id (str): The ID of the repository on the Hub.
        path_in_repo (str): The path to check within the repository (e.g., "filings/").
        repo_type (str, optional): The type of the repository. Defaults to "dataset".

    Returns:
        bool: True if the path exists, False otherwise.
    """
    try:
        # list_repo_files will error if the repo doesn't exist
        files = list_repo_files(repo_id=repo_id, repo_type=repo_type)

        # Check if any file in the repository starts with the desired path
        # This works for both files and folders.
        path_prefix = path_in_repo.strip("/")
        for f in files:
            if f.startswith(path_prefix):
                logger.info(f"Path '{path_in_repo}' found on Hugging Face Hub.")
                return True

        logger.warning(f"Path '{path_in_repo}' not found on Hugging Face Hub.")
        return False
    except Exception as e:
        logger.error(f"Could not check repository '{repo_id}': {e}")
        # If we can't check, assume it doesn't exist to be safe
        return False
