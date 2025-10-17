from __future__ import annotations

from typing import Dict, Any

from app.domain.status import (
  get_status_service,
  get_status_provider,
  set_status_provider,
  configure_default_status_provider,
)
from app.domain.status.interfaces import StatusProviderProtocol as IDataProvider
from app.domain.status.providers import (
  SimStatusProvider as SimDataProvider,
  ProductionStatusProvider as CommDataProvider,
)


def set_provider(provider: IDataProvider) -> None:
  set_status_provider(provider)


def get_provider() -> IDataProvider:
  return get_status_provider()


def get_status_payload() -> Dict[str, Any]:
  return get_status_service().fetch_status()


# Ensure default provider available for legacy callers at import time.
configure_default_status_provider()
