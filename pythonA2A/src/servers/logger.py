import logging
import os
from pathlib import Path
from typing import Optional


def get_logger(
    name: str,
    level: Optional[str] = None,
    filename: Optional[str] = None,
) -> logging.Logger:
    """
    Return a configured logger instance.

    Log level precedence:
    1) Function argument `level`
    2) Environment variable `LOG_LEVEL`
    3) Default: INFO
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    raw_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    log_level = getattr(logging, raw_level, logging.INFO)

    logger.setLevel(log_level)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if filename:
        target = Path(filename)
        target.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(target, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
