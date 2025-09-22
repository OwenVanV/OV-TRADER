"""Logging utilities for OV Trader."""

from __future__ import annotations

import logging
from logging import Logger
from typing import Optional


def configure_logging(level: int = logging.INFO) -> Logger:
    """Configure and return the project-wide logger.

    Parameters
    ----------
    level:
        Logging level.  Defaults to :data:`logging.INFO`.
    """

    logger = logging.getLogger("ov_trader")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
