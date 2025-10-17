"""Service layer orchestrating status data retrieval and augmentation."""

from __future__ import annotations

from typing import Dict, Any, Optional, Callable

from .repository import StatusRepository


class StatusService:
  """High-level status service consumed by HTTP/WS handlers."""

  def __init__(
      self,
      repository: StatusRepository,
      *,
      enrich_hook: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
  ) -> None:
    self._repository = repository
    self._enrich_hook = enrich_hook

  @property
  def repository(self) -> StatusRepository:
    return self._repository

  def set_enrich_hook(
      self, hook: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]]
  ) -> None:
    self._enrich_hook = hook

  def fetch_status(self) -> Dict[str, Any]:
    payload = self._repository.get_status()
    if self._enrich_hook is not None:
      try:
        payload = self._enrich_hook(payload)
      except Exception:
        # Keep payload untouched if enrichment fails.
        pass
    return payload
