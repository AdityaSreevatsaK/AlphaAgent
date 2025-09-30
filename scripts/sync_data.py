import sys
from pathlib import Path

from src.utils.config import DATA_DIR, get_config, MODELS_DIR
from src.utils.hub_manager import upload_to_hub
from src.utils.logger_config import setup_logging

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

# Setup logging
logger = setup_logging()

# --- Configuration for All Project Artefacts ---
DIRECTORIES_TO_SYNC = {
    "data": {"local_path": DATA_DIR, "hub_path": "data/"},
    "models": {"local_path": MODELS_DIR, "hub_path": "models/"},
}

# --- Main Execution ---
if __name__ == "__main__":
    huggingface_config = get_config("huggingface")
    if not huggingface_config or "repo_id" not in huggingface_config:
        logger.error("Hugging Face 'repo_id' not found in config.yml. Aborting sync.")
        sys.exit(1)

    repo_id = huggingface_config["repo_id"]
    logger.info(f"Starting data and artefact sync for repository: {repo_id}")

    # --- Sync All Configured Directories ---
    logger.info("--- Starting Directory Sync ---")
    for name, paths in DIRECTORIES_TO_SYNC.items():
        local_dir = paths["local_path"]

        if local_dir.exists() and local_dir.is_dir():
            # The log message will now simply say "data" or "models"
            logger.info(f"Preparing to sync directory '{name}' from '{local_dir}'...")

            upload_to_hub(
                repo_id=repo_id,
                local_dir_name=str(local_dir),
                path_in_repo=paths["hub_path"],
            )
        else:
            logger.warning(
                f"Local directory '{local_dir}' not found. Skipping sync for '{name}'."
            )

    logger.info("Data and artefact synchronisation process finished.")
