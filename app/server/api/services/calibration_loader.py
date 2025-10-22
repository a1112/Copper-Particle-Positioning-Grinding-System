from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping


class CalibrationSettingsLoader:
    """Load camera/workspace calibration data from the configs directory."""

    def __init__(self, configs_root: str | Path | None = None, filename: str = "calibration.json") -> None:
        base = Path(__file__).resolve().parents[4]
        default_dir = base / "configs"
        self._configs_dir = Path(configs_root) if configs_root else default_dir
        self._path = self._configs_dir / filename

    def load(self) -> Dict[str, Any]:
        payload = self._read_file()
        return self._normalize(payload)

    # Internals -----------------------------------------------------------------

    def _read_file(self) -> Dict[str, Any]:
        if not self._path.exists():
            return {}
        try:
            text = self._path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = self._path.read_text(encoding="gbk", errors="ignore")
        try:
            data = json.loads(text)
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

    def _normalize(self, data: Mapping[str, Any]) -> Dict[str, Any]:
        image = self._coerce_point(data.get("image") or data.get("image_size"), default=(0, 0))
        world = self._coerce_point(data.get("world") or data.get("world_size"), default=(0.0, 0.0))
        origin = self._coerce_point(data.get("origin") or {}, default=(0.0, 0.0))

        fixtures_raw = data.get("fixtures")
        fixtures: List[Dict[str, Any]] = []
        if isinstance(fixtures_raw, list):
            for item in fixtures_raw:
                fixture = self._normalize_fixture(item)
                if fixture is not None:
                    fixtures.append(fixture)

        return {
            "image": {"width": image[0], "height": image[1]},
            "world": {"width": world[0], "height": world[1]},
            "origin": {"x": origin[0], "y": origin[1]},
            "fixtures": fixtures,
        }

    def _normalize_fixture(self, payload: Any) -> Dict[str, Any] | None:
        if not isinstance(payload, Mapping):
            return None
        name = str(payload.get("name") or payload.get("id") or "")
        rotation = self._coerce_point(payload.get("rotation_origin") or payload.get("rotationOrigin") or {}, default=(0.0, 0.0))
        rect = self._coerce_rect(payload.get("rect") or payload.get("rectangle") or payload)
        return {
            "name": name,
            "rotation_origin": {"x": rotation[0], "y": rotation[1]},
            "rect": rect,
        }

    @staticmethod
    def _coerce_point(value: Any, *, default: tuple[float, float]) -> tuple[float, float]:
        if isinstance(value, Mapping):
            x = CalibrationSettingsLoader._to_float(value.get("x"), default[0])
            y = CalibrationSettingsLoader._to_float(value.get("y"), default[1])
            return x, y
        if isinstance(value, (list, tuple)) and len(value) >= 2:
            x = CalibrationSettingsLoader._to_float(value[0], default[0])
            y = CalibrationSettingsLoader._to_float(value[1], default[1])
            return x, y
        return default

    @staticmethod
    def _coerce_rect(value: Any) -> Dict[str, float]:
        if isinstance(value, Mapping):
            x = CalibrationSettingsLoader._to_float(value.get("x"), 0.0)
            y = CalibrationSettingsLoader._to_float(value.get("y"), 0.0)
            width = CalibrationSettingsLoader._to_float(value.get("width"), 0.0)
            height = CalibrationSettingsLoader._to_float(value.get("height"), 0.0)
        else:
            x = y = 0.0
            width = height = 0.0
        return {"x": x, "y": y, "width": width, "height": height}

    @staticmethod
    def _to_float(value: Any, fallback: float) -> float:
        try:
            return float(value)
        except Exception:
            return fallback


__all__ = ["CalibrationSettingsLoader"]
