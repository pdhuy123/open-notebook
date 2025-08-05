import logging
import sys

from typing import Union


def setup_logger(
    log_file: str = "local-rag.log", level: Union[int, str] = logging.INFO
):
    """
    Sets up a logger for this module.

    Args:
        log_file (str, optional): The file to which the logs should be written. Defaults to "local-rag.log".
        level (str, optional): The logging level at which to log messages. Defaults to logging.INFO.

    Returns:
        logging.Logger: The set up logger.

    Notes:
        This function sets up a logger for this module using the `logging` library. It sets the logging level to the specified level, and adds handlers for both file and console output with UTF-8 encoding. The log file can be customized by passing a different name as the argument.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)

    # Console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(level)
    if hasattr(console_handler.stream, "reconfigure"):
        console_handler.stream.reconfigure(encoding="utf-8")
    else:
        # Fallback for older Python versions or unsupported streams
        console_handler.stream = open(sys.stdout.fileno(), mode='w', encoding='utf-8', errors='backslashreplace')

    log_format = logging.Formatter(
        "%(asctime)s - %(module)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


log = setup_logger()