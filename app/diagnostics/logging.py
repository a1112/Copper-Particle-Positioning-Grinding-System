import logging
from typing import Optional


def _ensure_stream_handler(level: int = logging.INFO) -> None:
    """Ensure root logger has a single stream handler with our format."""
    root = logging.getLogger()
    for h in root.handlers:
        if isinstance(h, logging.StreamHandler):
            return
    h = logging.StreamHandler()
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
    h.setFormatter(fmt)
    root.addHandler(h)
    root.setLevel(level)


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Get a named logger with sane default formatting.

    Ensures a root StreamHandler exists once to avoid duplicate outputs.
    """
    _ensure_stream_handler()
    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    return logger

