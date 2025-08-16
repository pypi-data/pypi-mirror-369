# ankur_scraper/logging_config.py

import logging
import os
from rich.logging import RichHandler

# Create logs directory if it doesn't exist
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Define log file paths
INFO_LOG_FILE = os.path.join(LOG_DIR, "info.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")
GENERAL_LOG_FILE = os.path.join(LOG_DIR, "general.log")

# Create loggers
loggers = {
    "info": logging.getLogger("info_logger"),
    "error": logging.getLogger("error_logger"),
    "general": logging.getLogger("general_logger"),
}

# Set log levels
loggers["info"].setLevel(logging.INFO)
loggers["error"].setLevel(logging.ERROR)
loggers["general"].setLevel(logging.WARNING)  # Covers warnings, successes, etc.

# Log format for file
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# File handlers
info_handler = logging.FileHandler(INFO_LOG_FILE, encoding="utf-8")
info_handler.setFormatter(file_formatter)

error_handler = logging.FileHandler(ERROR_LOG_FILE, encoding="utf-8")
error_handler.setFormatter(file_formatter)

general_handler = logging.FileHandler(GENERAL_LOG_FILE, encoding="utf-8")
general_handler.setFormatter(file_formatter)

# Rich (terminal) handler
console_handler = RichHandler(
    rich_tracebacks=True,
    markup=True,  # Enables [bold], [green], etc.
)
console_handler.setLevel(logging.INFO)

# Attach handlers
loggers["info"].addHandler(info_handler)
loggers["info"].addHandler(console_handler)

loggers["error"].addHandler(error_handler)
loggers["error"].addHandler(console_handler)

loggers["general"].addHandler(general_handler)
loggers["general"].addHandler(console_handler)

# Prevent propagation to root logger
for logger in loggers.values():
    logger.propagate = False

# Logger accessor
def get_logger(log_type: str):
    return loggers.get(log_type, loggers["general"])
