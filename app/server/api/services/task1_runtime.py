from __future__ import annotations

from functools import lru_cache

from app.vision.task1.service import Task1Runner


@lru_cache(maxsize=1)
def get_task1_runner() -> Task1Runner:
    """Return a singleton Task1Runner shared across API modules."""
    return Task1Runner()


__all__ = ["get_task1_runner"]
