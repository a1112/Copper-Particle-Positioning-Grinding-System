from __future__ import annotations

import time
from typing import Any, Dict, Iterable, Optional

from app.domain.status.providers.sim import SimStatusProvider


class VirtualParameterDevice:
    """Lightweight simulated device that surfaces virtual machine parameters."""

    def __init__(self, provider: Optional[SimStatusProvider] = None) -> None:
        self._provider = provider or SimStatusProvider()
        self._latest_snapshot: Dict[str, Any] = {}
        self._latest_summary: Optional[Dict[str, Any]] = None

    @property
    def provider(self) -> SimStatusProvider:
        return self._provider

    def snapshot(self) -> Dict[str, Any]:
        """Return a cached snapshot while keeping the provider as the source of truth."""
        self._latest_snapshot = self._provider.get_status()
        return self._latest_snapshot

    def stream(self, count: Optional[int] = None, interval: float = 0.25) -> Iterable[Dict[str, Any]]:
        """
        Yield successive snapshots. Useful for tests or background simulators.

        Parameters
        ----------
        count:
            Number of snapshots to yield. ``None`` means infinite stream.
        interval:
            Sleep seconds between snapshots to mimic pacing.
        """
        produced = 0
        while count is None or produced < count:
            yield self.snapshot()
            produced += 1
            time.sleep(interval)

    def update_path_summary(self, summary: Dict[str, Any]) -> None:
        """Expose a path summary to both the device and the underlying status provider."""
        self._latest_summary = summary
        self._provider.update_extra_status(simulatedPath=summary)

    @property
    def latest_summary(self) -> Optional[Dict[str, Any]]:
        return self._latest_summary

