import logging

from src.utils import config


def setup_logging():
    """
    Sets up a centralized logger for the AlphaAgent project.
    """
    # Configure the logging format
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure the file handler
    file_handler = logging.FileHandler(config.LOG_FILE_PATH)
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.INFO)  # Only logs INFO level and above to the file

    # Configure the console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(
        logging.DEBUG
    )  # Logs all levels (DEBUG and above) to console

    # Get the root logger and add the handlers
    log_agent = logging.getLogger()
    log_agent.setLevel(logging.DEBUG)  # Set the root logger level to the lowest level
    log_agent.addHandler(file_handler)
    log_agent.addHandler(console_handler)

    return log_agent


logger = setup_logging()
