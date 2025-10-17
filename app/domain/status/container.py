"""Lightweight container for status service/provider wiring."""

from __future__ import annotations

from typing import Optional

from .interfaces import StatusProviderProtocol
from .repository import StatusRepository
from .service import StatusService
from .providers.sim import SimStatusProvider

_status_provider: Optional[StatusProviderProtocol] = None
_status_service: Optional[StatusService] = None


def configure_default_status_provider() -> None:
  """Ensure a provider/service exist (defaults to the simulator)."""
  global _status_provider, _status_service
  if _status_provider is None:
    _status_provider = SimStatusProvider()
  if _status_service is None:
    _status_service = StatusService(StatusRepository(_status_provider))


def set_status_provider(provider: StatusProviderProtocol) -> None:
  """Inject a new provider instance and rebuild the service layer."""
  global _status_provider, _status_service
  _status_provider = provider
  _status_service = StatusService(StatusRepository(provider))


def get_status_provider() -> StatusProviderProtocol:
  configure_default_status_provider()
  assert _status_provider is not None
  return _status_provider


def get_status_service() -> StatusService:
  configure_default_status_provider()
  assert _status_service is not None
  return _status_service
