"""Centralized application logging configuration."""

import logging
import sys


def setup_logging():
    """Configure structured console logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # Quiet down external loggers if needed
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
