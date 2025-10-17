"""Interfaces and type contracts for the status domain."""

from __future__ import annotations

from typing import Dict, Protocol, Any


class StatusProviderProtocol(Protocol):
  """Abstract provider returning machine/device status snapshots."""

  def get_status(self) -> Dict[str, Any]:
    """Return the latest status payload consumable by the API layer."""
    ...
