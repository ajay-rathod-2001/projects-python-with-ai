"""
Application Logger Setup
"""

import logging
from pathlib import Path
from backend.src.config.setting import LOG_FILE_PATH


def setup_logger() -> logging.Logger:
    LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("PhonePeTracker")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(name)s - %(message)s")

        # Rotating/Standard File Handler
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Stream Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

