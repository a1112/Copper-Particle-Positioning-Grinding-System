"""Global configuration helpers.

This module centralizes feature flags and environment-driven settings
so both API and UI can share the same toggles.
"""

from __future__ import annotations

import os
import socket
from pathlib import Path
from typing import Optional

try:  # optional dependency used to locate bundled balsam.exe
    import PySide6  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    PySide6 = None  # type: ignore[assignment]


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


def _env_int(name: str, default: int) -> int:
    val = _env_text(name)
    if val is None:
        return default
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


# DEBUG flag: enable extra logging/diagnostics across API and UI.
# Priority: COPPER_DEBUG > DEBUG > default False
DEBUG: bool = _env_bool("COPPER_DEBUG", _env_bool("DEBUG", False))
if socket.gethostname() in ['lcx_ace']:
    DEBUG = True
# DATA MODE flag: determines whether simulated ("sim") or runtime/production ("runtime") backends are used.
_DATA_MODE_RAW = _env_text("COPPER_DATA_MODE", _env_text("COPPER_RUNTIME_MODE", "http")) or "sim"
DATA_MODE: str = _DATA_MODE_RAW.lower()

# Optional endpoint for runtime/production data fetching.
DATA_ENDPOINT: Optional[str] = _env_text("COPPER_DATA_ENDPOINT")

# gRPC bridge configuration (used when DATA_MODE == "rpc").
RPC_LISTEN_ENDPOINT: str = _env_text("COPPER_RPC_LISTEN", "tcp://127.0.0.1:4242") or "tcp://127.0.0.1:4242"
RPC_CONTROL_ENDPOINT: str = _env_text("COPPER_RPC_CONTROL", "tcp://127.0.0.1:4243") or "tcp://127.0.0.1:4243"
RPC_TIMEOUT: float = _env_float("COPPER_RPC_TIMEOUT", 5.0)

# Project paths and API server defaults shared by server modules.
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
TEST_DATA_DIR: Path = PROJECT_ROOT / "TestData"
SAVE_DATA_ROOT: Path = Path(_env_text("COPPER_SAVE_DATA_ROOT", r"D:\SaveData") or r"D:\SaveData")
SAVE_DATA_RECORDS_DIR: Path = SAVE_DATA_ROOT / "record"
SAVE_DATA_CURRENT_DIR: Path = SAVE_DATA_ROOT / "current"
SAVE_DATA_ALG_RESULT_PATH: Path = Path(_env_text("COPPER_ALG_RESULT_PATH", str(SAVE_DATA_ROOT / "alg_result.json")) or str(SAVE_DATA_ROOT / "alg_result.json"))
SAVE_DATA_BALSAM_PATH: Optional[Path] = None
_balsam_env = _env_text("COPPER_BALSAM_PATH")
if _balsam_env:
    SAVE_DATA_BALSAM_PATH = Path(_balsam_env)
else:
    default_balsam = None
    if PySide6 is not None:
        pyside_balsam = Path(PySide6.__file__).with_name("balsam.exe")
        if pyside_balsam.exists():
            default_balsam = pyside_balsam
    if default_balsam is None:
        fallback_balsam = PROJECT_ROOT / "bin" / "balsam.exe"
        if fallback_balsam.exists():
            default_balsam = fallback_balsam
    SAVE_DATA_BALSAM_PATH = default_balsam

# API host/port/log-level used by uvicorn when running the public API.
APP_HOST: str = _env_text("COPPER_APP_HOST", "127.0.0.1") or "127.0.0.1"
APP_PORT: int = _env_int("COPPER_APP_PORT", 8010)
LOG_LEVEL: str = _env_text("COPPER_LOG_LEVEL", "debug" if DEBUG else "info") or ("debug" if DEBUG else "info")

# HTTP bridge configuration (used when DATA_MODE == "http").
HTTP_BRIDGE_BASE: str = _env_text("COPPER_HTTP_BRIDGE_BASE", f"http://{APP_HOST}:{APP_PORT}/bridge") or f"http://{APP_HOST}:{APP_PORT}/bridge"
HTTP_CONTROL_ENDPOINT: str = _env_text("COPPER_HTTP_CONTROL", "http://127.0.0.1:9001/control") or "http://127.0.0.1:9001/control"
HTTP_TIMEOUT: float = _env_float("COPPER_HTTP_TIMEOUT", RPC_TIMEOUT)

# Legacy attribute aliases expected by server modules.
testFolder: Path = TEST_DATA_DIR
app_host: str = APP_HOST
app_port: int = APP_PORT
log_level: str = LOG_LEVEL
data_mode: str = DATA_MODE
data_endpoint: Optional[str] = DATA_ENDPOINT
http_bridge_base: str = HTTP_BRIDGE_BASE
http_control_endpoint: str = HTTP_CONTROL_ENDPOINT
http_timeout: float = HTTP_TIMEOUT


def is_sim_mode() -> bool:
    """Return True when the application should use simulated devices/business services."""
    return DATA_MODE not in {"runtime", "production", "prod", "comm", "rpc", "http"}
