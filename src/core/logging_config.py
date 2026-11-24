"""Centralized logging configuration for MetroGraph Analytics."""

import logging
import sys

from src.core.settings import LOGS_DIR


def configure_logging(
    log_level: int = logging.INFO,
    log_file_name: str = "metrograph.log",
) -> logging.Logger:
    """Configures application-wide logging with both file and console handlers.

    Logs application startup, data loading, graph construction, and errors
    without exposing sensitive credentials or raw stack traces to end users.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file_path = LOGS_DIR / log_file_name

    logger = logging.getLogger("metrograph")
    logger.setLevel(log_level)

    # Avoid adding duplicate handlers if reconfigured
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "metrograph") -> logging.Logger:
    """Retrieves a named logger instance adhering to project standards."""
    return logging.getLogger(name)
