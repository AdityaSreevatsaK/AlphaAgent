# Import the specific function and config utilities you need
from src.utils.hub_manager import upload_to_hub
from src.utils.config import HF_DATA_REPO_ID, DATA_DIR
from src.utils.logger_config import logger


# --- Configuration ---
# Define the datasets to synchronise.
# 'local_dir_name' is the folder name inside the project's 'data' directory.
# 'hub_path' is the destination path in the Hugging Face Hub repository.
DATASETS_TO_SYNC = {
    "raw_filings": {"local_dir_name": "raw/filings", "hub_path": "raw/filings/"},
    "raw_news": {"local_dir_name": "raw/news", "hub_path": "raw/news/"},
    "processed_filings": {
        "local_dir_name": "processed/filings",
        "hub_path": "processed/filings/",
    },
    "processed_news": {
        "local_dir_name": "processed/news",
        "hub_path": "processed/news/",
    },
}

# --- Main Execution ---
if __name__ == "__main__":
    # Load the Hugging Face repository ID from the main config file.
    repo_id = HF_DATA_REPO_ID
    logger.info(f"Starting data sync for repository: {repo_id}")

    # Iterate over the defined datasets and synchronise each one.
    for name, paths in DATASETS_TO_SYNC.items():
        local_dir_name = paths["local_dir_name"]
        local_path = DATA_DIR / local_dir_name

        # Check if the local directory exists before attempting to sync.
        if local_path.exists() and local_path.is_dir():
            logger.info(
                f"Preparing to sync '{name}' from '{local_path}' to '{paths['hub_path']}'..."
            )

            # Call the upload_to_hub function directly from the hub_manager module.
            upload_to_hub(
                repo_id=repo_id,
                local_dir_name=local_dir_name,
                path_in_repo=paths["hub_path"],
            )
        else:
            # Log a warning if a configured local directory does not exist.
            logger.warning(
                f"Local directory '{local_path}' not found. Skipping sync for '{name}'."
            )

    logger.info("Data synchronisation process finished.")
