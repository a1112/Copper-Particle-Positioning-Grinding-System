"""Global configuration helpers.

This module centralizes feature flags and environment-driven settings
so both API and UI can share the same toggles.
"""

from __future__ import annotations

import os
from typing import Optional


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    val = val.strip().lower()
    return val in {"1", "true", "yes", "on"}


def _env_text(name: str, default: Optional[str] = None) -> Optional[str]:
    val = os.getenv(name)
    if val is None:
        return default
    val = val.strip()
    return val or default


def _env_float(name: str, default: float) -> float:
    val = _env_text(name)
    if val is None:
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


# DEBUG flag: enable extra logging/diagnostics across API and UI.
# Priority: COPPER_DEBUG > DEBUG > default False
DEBUG: bool = _env_bool("COPPER_DEBUG", _env_bool("DEBUG", False))

# DATA MODE flag: determines whether simulated ("sim") or runtime/production ("runtime") backends are used.
_DATA_MODE_RAW = _env_text("COPPER_DATA_MODE", _env_text("COPPER_RUNTIME_MODE", "rpc")) or "sim"
DATA_MODE: str = _DATA_MODE_RAW.lower()

# Optional endpoint for runtime/production data fetching.
DATA_ENDPOINT: Optional[str] = _env_text("COPPER_DATA_ENDPOINT")

# ZeroRPC bridge configuration (used when DATA_MODE == "rpc").
RPC_LISTEN_ENDPOINT: str = _env_text("COPPER_RPC_LISTEN", "tcp://127.0.0.1:4242") or "tcp://127.0.0.1:4242"
RPC_CONTROL_ENDPOINT: str = _env_text("COPPER_RPC_CONTROL", "tcp://127.0.0.1:4243") or "tcp://127.0.0.1:4243"
RPC_TIMEOUT: float = _env_float("COPPER_RPC_TIMEOUT", 5.0)


def is_sim_mode() -> bool:
    """Return True when the application should use simulated devices/business services."""
    return DATA_MODE not in {"runtime", "production", "prod", "comm", "rpc"}

