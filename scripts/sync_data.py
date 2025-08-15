from src.utils import config
from src.utils.config import HF_DATA_REPO_ID
from src.utils.hub_manager import check_hub_path_exists, get_from_hub, upload_to_hub
from src.utils.logger_config import logger

# --- Configuration ---
DATASETS_TO_SYNC = {
    "filings": {"local_dir": "raw/filings", "hub_path": "filings/"},
    "news": {"local_dir": "raw/news", "hub_path": "news/"},
}


def main():
    """
    Automated script to synchronize local data with the Hugging Face Hub.

    For each dataset, it checks the local and remote status and then decides
    to upload, download, or do nothing.
    """
    logger.info("Starting automated data synchronization process...")

    for name, paths in DATASETS_TO_SYNC.items():
        logger.info(f"--- Processing dataset: {name} ---")

        # Check local status
        local_path = config.DATA_DIR / paths["local_dir"]
        local_exists = local_path.exists() and any(local_path.iterdir())

        # Check remote (Hub) status
        hub_exists = check_hub_path_exists(
            repo_id=HF_DATA_REPO_ID, path_in_repo=paths["hub_path"]
        )

        # --- Automated Decision Logic ---
        if local_exists and not hub_exists:
            logger.info(f"Local '{name}' data found but not on Hub. Uploading...")
            upload_to_hub(
                repo_id=HF_DATA_REPO_ID,
                local_dir_name=paths["local_dir"],
                path_in_repo=paths["hub_path"],
            )
        elif not local_exists and hub_exists:
            logger.info(
                f"Local '{name}' data not found but exists on Hub. Downloading..."
            )
            get_from_hub(repo_id=HF_DATA_REPO_ID, local_dir_name=paths["local_dir"])
        elif local_exists and hub_exists:
            logger.info(
                f"Dataset '{name}' exists both locally and on the Hub. Sync complete."
            )
        else:  # Not local, not on Hub
            logger.warning(
                f"Dataset '{name}' not found locally or on the Hub. "
                f"Please run the appropriate fetch script (e.g., fetch_sec_data.py) first."
            )

    logger.info("--- Data synchronization process finished. ---")


if __name__ == "__main__":
    main()
