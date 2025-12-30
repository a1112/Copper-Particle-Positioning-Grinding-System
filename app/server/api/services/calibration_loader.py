from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET

from app import config as APP_CONFIG

log = logging.getLogger(__name__)


@dataclass
class _ImageInfo:
    width: float = 0.0
    height: float = 0.0


@dataclass
class _Fixture:
    name: str
    x: float
    y: float
    width: float
    height: float

    @property
    def rotation_origin(self) -> tuple[float, float]:
        return (self.x + self.width / 2.0, self.y + self.height / 2.0)


class CalibrationSettingsLoader:
    """Build calibration metadata from annotated assets in configs/calibration/."""

    def __init__(self, calibration_root: str | Path | None = None) -> None:
        default_dir = APP_CONFIG.CALIBRATION_DIR
        self._calibration_dir = Path(calibration_root) if calibration_root else default_dir

    # Public API ----------------------------------------------------------------

    def load(self) -> Dict[str, Any]:
        if not self._calibration_dir.exists():
            log.warning("Calibration directory missing: %s", self._calibration_dir)
            return {}

        xml_files = sorted(self._calibration_dir.glob("*.xml"))
        if not xml_files:
            log.warning("No annotation XML files found in calibration directory: %s", self._calibration_dir)
            return {}

        image_info: Optional[_ImageInfo] = None
        fixtures: List[_Fixture] = []
        for xml_path in xml_files:
            parsed_image, parsed_fixtures = self._parse_annotation(xml_path)
            if parsed_image is not None and image_info is None:
                image_info = parsed_image
            fixtures.extend(parsed_fixtures)

        if image_info is None:
            image_info = _ImageInfo()

        payload = {
            "image": {
                "width": float(image_info.width),
                "height": float(image_info.height),
            },
            # Without physical calibration data we fall back to pixel dimensions
            # so downstream code can still compute ratios.
            "world": {
                "width": float(image_info.width),
                "height": float(image_info.height),
            },
            "origin": {"x": 0.0, "y": 0.0},
            "fixtures": [
                {
                    "name": fixture.name,
                    "rotation_origin": {
                        "x": fixture.rotation_origin[0],
                        "y": fixture.rotation_origin[1],
                    },
                    "rect": {
                        "x": fixture.x,
                        "y": fixture.y,
                        "width": fixture.width,
                        "height": fixture.height,
                    },
                }
                for fixture in fixtures
            ],
        }
        return payload

    # Internals -----------------------------------------------------------------

    def _parse_annotation(self, xml_path: Path) -> tuple[Optional[_ImageInfo], List[_Fixture]]:
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except Exception as exc:
            log.warning("Failed to parse calibration annotation %s: %s", xml_path, exc)
            return None, []

        image_info = self._extract_image_info(root)
        fixtures = self._extract_fixtures(root, xml_path)
        return image_info, fixtures

    @staticmethod
    def _extract_image_info(root: ET.Element) -> Optional[_ImageInfo]:
        size_node = root.find("size")
        if size_node is None:
            return None
        try:
            width = float(size_node.findtext("width", default="0") or 0.0)
            height = float(size_node.findtext("height", default="0") or 0.0)
        except Exception:
            width = height = 0.0
        if width <= 0 or height <= 0:
            return None
        return _ImageInfo(width=width, height=height)

    def _extract_fixtures(self, root: ET.Element, xml_path: Path) -> List[_Fixture]:
        fixtures: List[_Fixture] = []
        for obj in root.findall("object"):
            name = (obj.findtext("name") or "").strip()
            if not name:
                log.debug("Annotation object without name in %s; skipping", xml_path)
                continue
            bbox = obj.find("bndbox")
            if bbox is None:
                log.debug("Annotation object %s missing bounding box in %s; skipping", name, xml_path)
                continue
            try:
                xmin = float(bbox.findtext("xmin", default="0"))
                ymin = float(bbox.findtext("ymin", default="0"))
                xmax = float(bbox.findtext("xmax", default="0"))
                ymax = float(bbox.findtext("ymax", default="0"))
            except Exception:
                log.debug("Invalid bounding box for %s in %s; skipping", name, xml_path)
                continue

            width = max(0.0, xmax - xmin)
            height = max(0.0, ymax - ymin)
            fixture = _Fixture(name=name, x=min(xmin, xmax), y=min(ymin, ymax), width=width, height=height)
            fixtures.append(fixture)
        return fixtures


__all__ = ["CalibrationSettingsLoader"]
