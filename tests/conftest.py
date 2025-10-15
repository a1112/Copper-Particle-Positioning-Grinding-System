from __future__ import annotations

import sys
from typing import Generator

import pytest
from fastapi.testclient import TestClient


def _bootstrap_app() -> "tuple[object, object]":
    # Import core app and prepare module aliases expected by route modules
    from app.server.api import api_core as core
    from app.server import CONFIG as real_config
    import app.db as app_db

    # Expose legacy module names used by route files
    sys.modules.setdefault("CONFIG", real_config)
    sys.modules.setdefault("db", app_db)

    # Import HTTP route modules so their routers get populated
    # Import ws modules (ws_status requires injected status_fn in tests)
    from app.server.api.api import api_config, api_image, api_motion, api_status, api_test  # noqa: F401
    from app.server.api.ws import ws_status, ws_logs  # noqa: F401

    # Attach routers to the FastAPI app (idempotent)
    core.include_router()
    return core.app, ws_status


@pytest.fixture(scope="session")
def app_and_ws() -> tuple[object, object]:
    return _bootstrap_app()


@pytest.fixture()
def client(app_and_ws: tuple[object, object]) -> Generator[TestClient, None, None]:
    app, _ = app_and_ws
    with TestClient(app) as c:
        yield c


