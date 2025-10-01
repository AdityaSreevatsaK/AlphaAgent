import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import HfApi, list_repo_files, login
from huggingface_hub import snapshot_download

from src.utils import config, logger_config

# Get the logger
logger = logger_config.setup_logging()


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
    # This is the final, correct path where data should be, e.g., '.../data/processed'
    final_data_path = config.DATA_DIR / local_dir_name

    # Check if the directory already exists and has content
    if final_data_path.exists() and any(final_data_path.iterdir()):
        logger.info(f"Data found locally at '{final_data_path}'. Skipping download.")
        return final_data_path

    logger.info(f"Data not found locally. Downloading from Hugging Face Hub: {repo_id}")

    try:
        # I'm downloading to the project's root directory. The `allow_patterns` will
        # ensure that huggingface_hub recreates the correct 'data/processed' structure.
        snapshot_download(
            repo_id=repo_id,
            repo_type=repo_type,
            local_dir=str(config.PROJECT_ROOT),
            allow_patterns=[f"data/{local_dir_name}/**"],
            local_dir_use_symlinks=False,
        )
        logger.info(f"Successfully downloaded data to '{final_data_path}'.")

    except Exception as e:
        logger.error(f"Failed to download data from {repo_id}. Error: {e}")
        raise

    return final_data_path


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
        f"Starting upload of directory '{local_dir_name}' to '{path_in_repo}' in repo '{repo_id}'..."
    )

    # --- Authentication ---
    load_dotenv()
    hf_token = os.getenv("HUGGINGFACE_ALPHA_AGENT_DATA_REPO_KEY")
    if not hf_token:
        logger.error(
            "Hugging Face token not found. Please add HUGGINGFACE_ALPHA_AGENT_DATA_REPO_KEY to your .env file."
        )
        return
    login(token=hf_token)

    # --- Path and Upload Logic ---
    # Assuming 'config.DATA_DIR' is defined in your project as the root data folder
    from src.utils.config import DATA_DIR

    local_path = DATA_DIR / local_dir_name

    if not local_path.exists() or not local_path.is_dir():
        logger.error(f"Local directory not found at '{local_path}'. Aborting upload.")
        return

    try:
        api = HfApi()
        api.upload_folder(
            folder_path=str(local_path),
            repo_id=repo_id,
            repo_type=repo_type,
            path_in_repo=path_in_repo,
        )
        logger.info(f"Directory '{local_dir_name}' uploaded successfully.")
    except Exception as e:
        logger.error(f"An error occurred during directory upload: {e}", exc_info=True)


def upload_file_to_hub(
    repo_id: str, local_file_path: str, path_in_repo: str, repo_type: str = "dataset"
):
    """
    Uploads a single local file to the Hugging Face Hub.

    Args:
        repo_id (str): The ID of the repository on the Hub.
        local_file_path (str): The full path to the local file to upload.
        path_in_repo (str): The target path (including filename) within the Hub repository.
        repo_type (str, optional): The type of the repository. Defaults to "dataset".
    """
    logger.info(
        f"Starting upload of file '{local_file_path}' to '{path_in_repo}' in repo '{repo_id}'..."
    )

    # --- Authentication ---
    load_dotenv()
    hf_token = os.getenv("HUGGINGFACE_ALPHA_AGENT_DATA_REPO_KEY")
    if not hf_token:
        logger.error(
            "Hugging Face token not found. Please add HUGGINGFACE_ALPHA_AGENT_DATA_REPO_KEY to your .env file."
        )
        return
    login(token=hf_token)

    # --- Path and Upload Logic ---
    if not Path(local_file_path).exists():
        logger.error(f"Local file not found at '{local_file_path}'. Aborting upload.")
        return

    try:
        api = HfApi()
        api.upload_file(
            path_or_fileobj=local_file_path,
            path_in_repo=path_in_repo,
            repo_id=repo_id,
            repo_type=repo_type,
        )
        logger.info(f"File '{path_in_repo}' uploaded successfully.")
    except Exception as e:
        logger.error(f"An error occurred during file upload: {e}", exc_info=True)
