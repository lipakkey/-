from __future__ import annotations

import logging
from pathlib import Path

LOG_ROOT = Path("logs")
LOG_ROOT.mkdir(parents=True, exist_ok=True)

_LOGGER_CACHE: dict[str, logging.Logger] = {}


def get_logger(name: str) -> logging.Logger:
    if name in _LOGGER_CACHE:
        return _LOGGER_CACHE[name]

    logger = logging.getLogger(f"desktop.{name}")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        log_file = LOG_ROOT / "desktop.log"
        handler = logging.FileHandler(log_file, encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    _LOGGER_CACHE[name] = logger
    return logger
