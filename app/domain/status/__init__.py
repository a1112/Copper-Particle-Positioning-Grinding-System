"""Status domain: service/data/provider layering for API & UI."""

from .service import StatusService
from .repository import StatusRepository
from .container import (
    get_status_service,
    set_status_provider,
    get_status_provider,
    configure_default_status_provider,
)

__all__ = [
    "StatusService",
    "StatusRepository",
    "get_status_service",
    "set_status_provider",
    "get_status_provider",
    "configure_default_status_provider",
]
