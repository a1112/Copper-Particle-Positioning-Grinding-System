"""Data layer for retrieving status snapshots from the configured provider."""

from __future__ import annotations

from typing import Dict, Any

from .interfaces import StatusProviderProtocol


class StatusRepository:
  """Repository responsible for fetching status data from a provider."""

  def __init__(self, provider: StatusProviderProtocol) -> None:
    self._provider = provider

  @property
  def provider(self) -> StatusProviderProtocol:
    return self._provider

  def set_provider(self, provider: StatusProviderProtocol) -> None:
    self._provider = provider

  def get_status(self) -> Dict[str, Any]:
    return self._provider.get_status()
