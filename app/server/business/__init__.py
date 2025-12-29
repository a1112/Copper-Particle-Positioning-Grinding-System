from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BusinessService
from .http import HttpBusinessService
from .runtime import RuntimeBusinessService
from .sim import SimBusinessService

if TYPE_CHECKING:  # pragma: no cover
    from .rpc import RpcBusinessService as RpcBusinessService


def __getattr__(name: str):
    if name == "RpcBusinessService":
        from .rpc import RpcBusinessService

        return RpcBusinessService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "BusinessService",
    "SimBusinessService",
    "RuntimeBusinessService",
    "RpcBusinessService",
    "HttpBusinessService",
]
