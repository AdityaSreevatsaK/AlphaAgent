import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

# --- Project Root ---
# Defines the absolute path to the project's root directory.
# This makes all other paths relative and the project portable.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# --- Load Environment Variables ---
load_dotenv()

# --- SEC EDGAR API Configuration ---
# User agent for making requests to the SEC.
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT")


def get_config(section: str) -> dict:
    """
    Reads a specific section from the config.yml file located in the project root.

    Args:
        section (str): The top-level key of the configuration section to retrieve.

    Returns:
        dict: A dictionary containing the configuration for the requested section.
              Returns an empty dict if the section or file is not found.
    """
    config_path = PROJECT_ROOT / "config.yml"
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        return config.get(section, {})
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        return {}
    except Exception as e:
        print(f"Error reading or parsing the configuration file: {e}")
        return {}


# --- Static Directory Paths ---
# Define key data directories relative to the project root.
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# --- Create Directories on Import ---
# This ensures that the necessary folders exist when the application starts.
DATA_DIR.mkdir(exist_ok=True)
RAW_DATA_DIR.mkdir(exist_ok=True)
PROCESSED_DATA_DIR.mkdir(exist_ok=True)
VECTOR_STORE_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# --- Logging Configuration ---
# A simple configuration for logging project activities.
LOGS_DIR = PROJECT_ROOT / "logs"
LOG_FILE_PATH = LOGS_DIR / "alpha_agent.log"

# --- Model Configuration ---
# For now, it's a placeholder, but we'll expand on this.
BASE_MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
ADAPTERS_PATH = PROJECT_ROOT / "models" / "fine_tuned_adapters"
