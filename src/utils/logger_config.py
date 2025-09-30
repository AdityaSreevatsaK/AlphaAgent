import logging

import coloredlogs

from src.utils import config


def setup_logging():
    """
    Sets up a centralized, colour-coded logger for the AlphaAgent project.
    """
    # Get the root logger
    log_agent = logging.getLogger()
    log_agent.setLevel(logging.DEBUG)

    # Clear any existing handlers to prevent duplicate logging
    if log_agent.hasHandlers():
        log_agent.handlers.clear()

    # --- Configure the File Handler (no colours) ---
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler = logging.FileHandler(config.LOG_FILE_PATH)
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.DEBUG)
    log_agent.addHandler(file_handler)

    # --- Configure the Console Handler using coloredlogs ---
    # This single line replaces the manual setup of the console_handler
    coloredlogs.install(
        level="DEBUG",
        logger=log_agent,
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    return log_agent


logger = setup_logging()
