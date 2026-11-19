"""Console logging and optional local file rotation."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from threading import Lock

from src.utils.paths import initialize_log_directory

_NAMESPACE = "smartroute"
_FORMATTER = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
_LOCK = Lock()


def configure_logging(
    level: str | int = logging.INFO,
    *,
    file_logging: bool = False,
    log_dir: Path | None = None,
) -> None:
    """Configure project handlers, falling back to console if file logging fails."""
    logger = get_logger()
    with _LOCK:
        logger.setLevel(level)
        logger.propagate = False
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

        console = logging.StreamHandler()
        console.setFormatter(_FORMATTER)
        logger.addHandler(console)
        if file_logging:
            try:
                directory = initialize_log_directory() if log_dir is None else log_dir
                directory.mkdir(parents=True, exist_ok=True)
                file_handler = RotatingFileHandler(
                    directory / "smartroute.log",
                    maxBytes=1_048_576,
                    backupCount=3,
                    encoding="utf-8",
                )
            except (OSError, ValueError):
                logger.warning("File logging unavailable. Continuing with console logging.")
            else:
                file_handler.setFormatter(_FORMATTER)
                logger.addHandler(file_handler)


def get_logger(module: str = "") -> logging.Logger:
    """Return a logger in the project namespace without configuring handlers."""
    name = f"{_NAMESPACE}.{module}" if module else _NAMESPACE
    return logging.getLogger(name)
