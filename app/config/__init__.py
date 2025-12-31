"""Global configuration helpers.

This module centralizes feature flags, paths, and connection settings so both
API and UI can share the same toggles and config defaults.
"""

from __future__ import annotations

import json
import os
import socket
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import quote_plus

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


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _quote(value: Optional[str]) -> str:
    if value is None:
        return ""
    return quote_plus(str(value))


# DEBUG flag: enable extra logging/diagnostics across API and UI.
# Priority: COPPER_DEBUG > DEBUG > default False
DEBUG: bool = _env_bool("COPPER_DEBUG", _env_bool("DEBUG", False))
if socket.gethostname() in ["lcx_ace"]:
    DEBUG = True

# DATA MODE flag: determines whether simulated ("sim") or runtime/production backends are used.
_DATA_MODE_RAW = _env_text("COPPER_DATA_MODE", _env_text("COPPER_RUNTIME_MODE", "http")) or "sim"
DATA_MODE: str = _DATA_MODE_RAW.lower()

# Optional endpoint for runtime/production data fetching.
DATA_ENDPOINT: Optional[str] = _env_text("COPPER_DATA_ENDPOINT")

# gRPC bridge configuration (used when DATA_MODE == "rpc").
RPC_LISTEN_ENDPOINT: str = _env_text("COPPER_RPC_LISTEN", "tcp://127.0.0.1:4242") or "tcp://127.0.0.1:4242"
RPC_CONTROL_ENDPOINT: str = _env_text("COPPER_RPC_CONTROL", "tcp://127.0.0.1:4243") or "tcp://127.0.0.1:4243"
RPC_TIMEOUT: float = _env_float("COPPER_RPC_TIMEOUT", 5.0)

# Project paths and API server defaults shared by server modules.
PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
CONFIGS_DIR: Path = PROJECT_ROOT / "configs"
CALIBRATION_DIR: Path = CONFIGS_DIR / "calibration"
TEMPLATE_DIR: Path = CONFIGS_DIR / "template"
CALIBRATION_STATE_PATH: Path = CALIBRATION_DIR / "calibration.json"
CALIBRATION_TEMPLATE_ANNOTATION: Path = TEMPLATE_DIR / "src_IMG_Color.xml"
SERVER_CONFIG_PATH: Path = CONFIGS_DIR / "server.json"
DATABASE_CONFIG_PATH: Path = CONFIGS_DIR / "database_config.yaml"

TEST_DATA_DIR: Path = PROJECT_ROOT / "TestData"
SAVE_DATA_ROOT: Path = Path(_env_text("COPPER_SAVE_DATA_ROOT", r"D:\SaveData") or r"D:\SaveData")
SAVE_DATA_RECORDS_DIR: Path = SAVE_DATA_ROOT / "record"
SAVE_DATA_CURRENT_DIR: Path = SAVE_DATA_ROOT / "current"

_default_alg_result = _env_text("COPPER_ALG_RESULT_PATH")
if _default_alg_result:
    _alg_result_path = Path(_default_alg_result)
else:
    candidate = SAVE_DATA_ROOT / "alg_result.json"
    if not candidate.exists():
        sample_alg = PROJECT_ROOT / "TestData" / "1" / "alg_result.json"
        if sample_alg.exists():
            candidate = sample_alg
    _alg_result_path = candidate
SAVE_DATA_ALG_RESULT_PATH: Path = _alg_result_path

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


def _database_defaults() -> Dict[str, Any]:
    return {
        "type": "mysql",
        "ip": "127.0.0.1",
        "port": 3306,
        "user": "remote_user",
        "password": "123456",
        "name": "MzPoliShineDB",
        "charset": "utf8mb4",
        "timezone": "+08:00",
    }


def _merge_database_settings() -> Dict[str, Any]:
    settings = _database_defaults()
    server_cfg = _read_json(SERVER_CONFIG_PATH)
    if isinstance(server_cfg.get("database"), dict):
        for key, value in server_cfg["database"].items():
            if value is not None:
                settings[key] = value

    settings["type"] = _env_text("COPPER_DB_TYPE", str(settings.get("type") or "")) or settings["type"]
    settings["ip"] = _env_text("COPPER_DB_IP", str(settings.get("ip") or "")) or settings["ip"]
    settings["port"] = _env_int("COPPER_DB_PORT", int(settings.get("port") or 0) or 3306)
    settings["user"] = _env_text("COPPER_DB_USER", str(settings.get("user") or "")) or settings["user"]
    settings["password"] = _env_text("COPPER_DB_PASSWORD", str(settings.get("password") or "")) or settings["password"]
    settings["name"] = _env_text("COPPER_DB_NAME", str(settings.get("name") or "")) or settings["name"]
    settings["charset"] = _env_text("COPPER_DB_CHARSET", str(settings.get("charset") or "")) or settings["charset"]
    settings["timezone"] = _env_text("COPPER_DB_TIMEZONE", str(settings.get("timezone") or "")) or settings["timezone"]
    return settings


def build_database_url(settings: Optional[Dict[str, Any]] = None) -> str:
    cfg = settings or _merge_database_settings()
    backend = str(cfg.get("type") or "mysql").lower()
    if "://" in backend:
        return backend

    if backend in {"mysql", "mariadb"}:
        scheme = "mysql+pymysql"
    elif backend in {"postgres", "postgresql"}:
        scheme = "postgresql"
    elif backend == "sqlite":
        scheme = "sqlite"
    else:
        scheme = backend

    if scheme.startswith("sqlite"):
        name = str(cfg.get("name") or ":memory:")
        if name == ":memory:":
            return "sqlite:///:memory:"
        return f"sqlite:///{name}"

    user = _quote(str(cfg.get("user") or ""))
    password = _quote(str(cfg.get("password") or ""))
    host = str(cfg.get("ip") or "127.0.0.1")
    port = int(cfg.get("port") or 3306)
    name = str(cfg.get("name") or "")

    auth = f"{user}:{password}@" if user or password else ""
    query: Dict[str, str] = {}
    charset = str(cfg.get("charset") or "").strip()
    if charset:
        query["charset"] = charset
    timezone = str(cfg.get("timezone") or "").strip()
    # NOTE:
    # - For MySQL/PyMySQL, passing `timezone` via the URL causes SQLAlchemy to
    #   forward it as a DBAPI kwarg, which newer PyMySQL versions do not accept.
    # - Time zone for MySQL is instead applied via `init_command` in
    #   `app.db.base._build_engine`. To avoid the TypeError, we only keep
    #   timezone in the URL for non-MySQL backends.
    if timezone and not scheme.startswith("mysql"):
        query["timezone"] = timezone
    query_str = "&".join(f"{k}={_quote(v)}" for k, v in query.items())
    suffix = f"?{query_str}" if query_str else ""
    return f"{scheme}://{auth}{host}:{port}/{name}{suffix}"


DATABASE_SETTINGS: Dict[str, Any] = _merge_database_settings()
DEFAULT_DB_URL: str = build_database_url(DATABASE_SETTINGS)
DATABASE_URL: Optional[str] = _env_text("DATABASE_URL", _env_text("COPPER_DATABASE_URL"))
PRIMARY_DB_URL: str = _env_text("PRIMARY_DB_URL", DEFAULT_DB_URL) or DEFAULT_DB_URL
LOCAL_DB_URL: str = _env_text("LOCAL_DB_URL", DEFAULT_DB_URL) or DEFAULT_DB_URL

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
