import os
from pathlib import Path

from dotenv import load_dotenv

# --- Load Environment Variables ---
# This line looks for a .env file in the project root and loads its variables.
load_dotenv()

# --- Project Root ---
# This gives us the absolute path to the project's root directory.
# We go up two levels from this file's location (src/utils/ -> src/ -> ROOT).
PROJECT_ROOT = Path(__file__).parent.parent.parent

# --- SEC EDGAR API Configuration ---
# Your user agent for making requests to the SEC.
# It's fetched from your .env file for security.
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT")

# --- Data Directories ---
# We define all data paths relative to the project root.
# This makes your project portable.
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"

# --- Model Configuration ---
# This is where you will define your model settings.
# For now, it's a placeholder, but you will expand on this.
BASE_MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
ADAPTERS_PATH = PROJECT_ROOT / "models" / "fine_tuned_adapters"

# --- Logging Configuration ---
# A simple configuration for logging project activities.
LOGS_DIR = PROJECT_ROOT / "logs"
LOG_FILE_PATH = LOGS_DIR / "alpha_agent.log"

# --- Create Directories if they don't exist ---
# This part of the script will automatically create the necessary folders when the config module is first imported.
DATA_DIR.mkdir(exist_ok=True)
RAW_DATA_DIR.mkdir(exist_ok=True)
PROCESSED_DATA_DIR.mkdir(exist_ok=True)
VECTOR_STORE_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# --- Data Fetching Configuration ---
HF_DATA_REPO_ID = "AdityaSreevatsaK/AlphaAgent-Data"
# Number of days of historical news to fetch
NEWS_LOOKBACK_DAYS = 90
