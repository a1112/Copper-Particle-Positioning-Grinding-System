from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Dict, Iterable, Mapping, Optional, Tuple


class PointCloudError(RuntimeError):
    """Raised when point cloud data cannot be accessed."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass
class _PointCloudBundle:
    arrays: Dict[str, "np.ndarray"]
    mtimes: Dict[str, float]
    shape: Tuple[int, int]


class PointCloudCache:
    """Caches structured-light point cloud rasters for current and historical records."""

    def __init__(
        self,
        current_dir: Path,
        records_dir: Path,
        filenames: Mapping[str, Path],
    ) -> None:
        self._current_dir = current_dir
        self._records_dir = records_dir
        self._filenames = dict(filenames)
        self._lock = RLock()
        self._bundles: Dict[Optional[int], _PointCloudBundle] = {}

    def clear(self) -> None:
        with self._lock:
            self._bundles.clear()

    def get_bundle(self, record_id: Optional[int]) -> _PointCloudBundle:
        key = record_id if record_id and record_id > 0 else None
        with self._lock:
            bundle = self._bundles.get(key)
            if bundle is not None and not self._has_changes(key, bundle):
                return bundle

        bundle = self._load_bundle(key)
        with self._lock:
            self._bundles[key] = bundle
        return bundle

    def _has_changes(self, key: Optional[int], bundle: _PointCloudBundle) -> bool:
        base = self._resolve_base(key)
        for axis, mtime in bundle.mtimes.items():
            file_path = base / self._filenames[axis].name
            if not file_path.exists():
                return True
            if file_path.stat().st_mtime != mtime:
                return True
        return False

    def _load_bundle(self, key: Optional[int]) -> _PointCloudBundle:
        base = self._resolve_base(key)
        arrays: Dict[str, "np.ndarray"] = {}
        mtimes: Dict[str, float] = {}
        shape: Tuple[int, int] | None = None

        try:
            import cv2
            import numpy as np
        except Exception as exc:  # pragma: no cover - dependency missing
            raise PointCloudError("Point cloud support unavailable", status_code=500) from exc

        for axis, filename in self._filenames.items():
            file_path = base / filename.name
            if not file_path.exists():
                message = (
                    f"Point cloud component '{filename.name}' not found "
                    f"in {'current' if key is None else f'record {key}'} directory"
                )
                raise PointCloudError(message, status_code=404)

            data = cv2.imread(str(file_path), cv2.IMREAD_UNCHANGED)
            if data is None:
                raise PointCloudError(f"Failed to load point cloud '{file_path}'", status_code=500)
            if data.ndim >= 3:
                data = data[:, :, 0]
            if data.dtype != np.float32:
                data = data.astype(np.float32, copy=False)

            arrays[axis] = data
            mtimes[axis] = file_path.stat().st_mtime
            if shape is None:
                shape = data.shape[:2]
            elif shape != data.shape[:2]:
                raise PointCloudError("Point cloud component dimensions mismatch", status_code=500)

        assert shape is not None
        return _PointCloudBundle(arrays=arrays, mtimes=mtimes, shape=shape)

    def _resolve_base(self, key: Optional[int]) -> Path:
        if key is None:
            if not self._current_dir.exists():
                raise PointCloudError(
                    f"Current save-data directory missing at {self._current_dir}", status_code=404
                )
            return self._current_dir
        target = self._records_dir / str(key)
        if not target.exists():
            raise PointCloudError(f"Record directory missing at {target}", status_code=404)
        return target


__all__ = ["PointCloudCache", "PointCloudError"]
