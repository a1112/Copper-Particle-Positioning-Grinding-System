from __future__ import annotations

from typing import Optional

from app.server.business import BusinessService

_backend: Optional[BusinessService] = None


def set_backend(service: BusinessService) -> None:
    global _backend
    _backend = service


def get_backend() -> BusinessService:
    global _backend
    if _backend is None:
        from app.server.business import SimBusinessService

        _backend = SimBusinessService()
    return _backend
