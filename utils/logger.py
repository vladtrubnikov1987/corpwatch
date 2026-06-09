import logging
import os

from config.settings import settings


def setup_logger() -> logging.Logger:
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

    logger = logging.getLogger("corpwatch")
    logger.setLevel(settings.LOG_LEVEL)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(settings.LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()