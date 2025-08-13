import logging
import os
import sys
from pathlib import Path

from vail.utils.env import load_env

# Load environment variables
load_env()

DEFAULT_LOG_LEVEL = logging.INFO

def get_log_dir() -> Path:
    """
    Get the log directory from environment variable or fallback to standard system location.
    On macOS, defaults to ~/Library/Logs/vail-model-registry/
    """
    # Try to get log directory from environment variable
    log_dir = os.getenv("LOG_DIR")
    if log_dir:
        return Path(log_dir).resolve()

    # Fallback to standard system location
    home_dir = Path.home()
    if os.name == "posix":  # macOS and Linux
        log_dir = home_dir / "Library" / "Logs" / "vail-model-registry"
    else:  # Windows
        log_dir = home_dir / "AppData" / "Local" / "vail-model-registry" / "logs"

    return log_dir


def setup_logging(log_file_name: str = "model_registry.log", level: int = DEFAULT_LOG_LEVEL):
    """
    Set up logging with both console and file handlers.

    Args:
        log_file_name: Name of the log file to create
    """
    # Get log directory
    log_dir = get_log_dir()
    log_dir.mkdir(exist_ok=True, parents=True)

    # Create logger
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger("vail_model_registry")
    logger.setLevel(logging.DEBUG)  # Set root logger level
    logger.propagate = False

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create file handler first (so initial messages go to file)
    log_file = log_dir / log_file_name
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # File shows DEBUG and above
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Log the directory info to file only
    logger.debug(f"Log directory: {log_dir}")

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level) # <<< This is controlled by the --verbose flag
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(console_handler)

    return logger
