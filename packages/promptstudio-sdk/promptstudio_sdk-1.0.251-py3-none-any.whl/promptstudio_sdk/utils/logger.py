import logging
import sys


def setup_logger():
    # Create logger
    logger = logging.getLogger("promptstudio")
    logger.setLevel(logging.INFO)

    # Create console handler and set level to INFO
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Add formatter to console handler
    console_handler.setFormatter(formatter)

    # Add console handler to logger if it doesn't already have handlers
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger
