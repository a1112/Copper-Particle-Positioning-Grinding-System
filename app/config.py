"""Global configuration helpers.

This module centralizes feature flags and environment-driven settings
so both API and UI can share the same toggles.
"""

from __future__ import annotations

import os


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    val = val.strip().lower()
    return val in {"1", "true", "yes", "on"}


# DEBUG flag: enable extra logging/diagnostics across API and UI.
# Priority: COPPER_DEBUG > DEBUG > default False
DEBUG: bool = _env_bool("COPPER_DEBUG", _env_bool("DEBUG", False))

