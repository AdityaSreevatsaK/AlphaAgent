import os

from dotenv import load_dotenv
from huggingface_hub import HfApi, login

from src.utils import config
from src.utils.logger_config import logger

# --- Configuration ---
# The ID of your repository on the Hugging Face Hub
HF_REPO_ID = "AdityaSreevatsaK/AlphaAgent-Data"
# The local directory you want to upload
LOCAL_DATA_DIR = config.RAW_DATA_DIR / "filings"


def main():
    """
    Uploads the contents of the local SEC filings directory to the Hugging Face Hub.

    This function performs the following steps:
        1. Loads the Hugging Face token from environment variables.
        2. Logs in to the Hugging Face Hub using the retrieved token.
        3. Initializes the Hugging Face Hub API client.
        4. Uploads the specified local directory (`LOCAL_DATA_DIR`) to the
            configured Hugging Face repository (`HF_REPO_ID`) as a dataset.
    """
    logger.info("Starting upload process to Hugging Face Hub...")

    # Load environment variables to get the token
    load_dotenv()
    hf_token = os.getenv("HUGGINGFACE_ALPHA_AGENT_DATA_REPO_KEY")
    if not hf_token:
        logger.error(
            "Hugging Face token not found. Please add HF_TOKEN to your .env file."
        )
        return

    # Log in to Hugging Face Hub
    login(token=hf_token)
    logger.info("Successfully logged in to Hugging Face Hub.")

    # Initialize the Hub API
    api = HfApi()

    # Upload the entire folder
    try:
        logger.info(
            f"Uploading directory '{LOCAL_DATA_DIR}' to repository '{HF_REPO_ID}'..."
        )
        api.upload_folder(
            folder_path=str(LOCAL_DATA_DIR),
            repo_id=HF_REPO_ID,
            repo_type="dataset",
            # This will create a 'filings' subfolder in your Hub repo
            path_in_repo="filings/",
        )
        logger.info("Upload completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during upload: {e}", exc_info=True)


if __name__ == "__main__":
    main()
