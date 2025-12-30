from __future__ import annotations

import json
import logging
import re
import shutil
import time
from functools import cached_property
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from app import config
from app.common import save_data
from .calibration_loader import CalibrationSettingsLoader

log = logging.getLogger(__name__)


_DEFAULT_COLOR_CANDIDATES = (
    "src_IMG_Color.png",
    "src_IMG_Texture_8Bit.png",
    "rts_ImageZ1ZeroReal.tif",
)

_DATA_FILENAME = "calibration_data.json"
_STATE_FILENAME = "calibration.json"


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)


def _sanitize_name(name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", name.strip())
    return safe or f"calib_{int(time.time())}"


def _best_existing_group(root: Path, exclude: Optional[str] = None) -> Optional[Path]:
    for item in sorted(root.iterdir()):
        if not item.is_dir():
            continue
        if exclude and item.name == exclude:
            continue
        return item
    return None


def _latest_record_id(records_root: Path) -> Optional[int]:
    if not records_root.exists():
        return None
    numeric_dirs = []
    for child in records_root.iterdir():
        if not child.is_dir():
            continue
        try:
            numeric_dirs.append(int(child.name))
        except ValueError:
            continue
    return max(numeric_dirs) if numeric_dirs else None


def _affine2d(points: list[dict[str, Any]]) -> list[list[float]]:
    """Solve 2D affine transform from pixel(x,y,1) to camera(x,y)."""
    src: list[tuple[float, float]] = []
    dst: list[tuple[float, float]] = []
    for pt in points:
        px = pt.get("pixel") or {}
        cam = pt.get("camera") or {}
        if px.get("x") is None or px.get("y") is None:
            continue
        if cam.get("x") is None or cam.get("y") is None:
            continue
        src.append((float(px["x"]), float(px["y"])))
        dst.append((float(cam["x"]), float(cam["y"])))
    if len(src) < 3:
        return []
    import numpy as np  # type: ignore

    A_rows = []
    b_rows = []
    for (x, y), (u, v) in zip(src, dst):
        A_rows.append([x, y, 1, 0, 0, 0])
        A_rows.append([0, 0, 0, x, y, 1])
        b_rows.append(u)
        b_rows.append(v)
    A = np.asarray(A_rows, dtype=float)
    b = np.asarray(b_rows, dtype=float)
    try:
        coeffs, *_ = np.linalg.lstsq(A, b, rcond=None)
    except Exception:
        return []
    a, b1, c, d, e, f = coeffs
    return [
        [float(a), float(b1), float(c)],
        [float(d), float(e), float(f)],
        [0.0, 0.0, 1.0],
    ]


def _affine3d(points: list[dict[str, Any]]) -> list[list[float]]:
    """Solve 3D affine transform (4x4) from camera to machine using least squares."""
    src: list[tuple[float, float, float]] = []
    dst: list[tuple[float, float, float]] = []
    for pt in points:
        cam = pt.get("camera") or {}
        mach = pt.get("machine") or {}
        if None in (cam.get("x"), cam.get("y"), cam.get("z")):
            continue
        if None in (mach.get("x"), mach.get("y"), mach.get("z")):
            continue
        src.append((float(cam["x"]), float(cam["y"]), float(cam["z"])))
        dst.append((float(mach["x"]), float(mach["y"]), float(mach["z"])))
    if len(src) < 4:
        return []
    import numpy as np  # type: ignore

    A_rows = []
    bx, by, bz = [], [], []
    for (x, y, z), (X, Y, Z) in zip(src, dst):
        A_rows.append([x, y, z, 1])
        bx.append(X)
        by.append(Y)
        bz.append(Z)
    A = np.asarray(A_rows, dtype=float)
    try:
        sol_x, *_ = np.linalg.lstsq(A, np.asarray(bx, dtype=float), rcond=None)
        sol_y, *_ = np.linalg.lstsq(A, np.asarray(by, dtype=float), rcond=None)
        sol_z, *_ = np.linalg.lstsq(A, np.asarray(bz, dtype=float), rcond=None)
    except Exception:
        return []
    mat = [
        [float(sol_x[0]), float(sol_x[1]), float(sol_x[2]), float(sol_x[3])],
        [float(sol_y[0]), float(sol_y[1]), float(sol_y[2]), float(sol_y[3])],
        [float(sol_z[0]), float(sol_z[1]), float(sol_z[2]), float(sol_z[3])],
        [0.0, 0.0, 0.0, 1.0],
    ]
    return mat


@dataclass
class CalibrationGroupOverview:
    name: str
    path: Path
    color_image: Optional[Path]
    annotation: Optional[Path]
    points_count: int
    created_at: float

    def to_dict(self, active_group: str | None) -> Dict[str, Any]:
        return {
            "name": self.name,
            "folder": str(self.path),
            "color_image": self.color_image.as_uri() if self.color_image else None,
            "annotation": self.annotation.as_uri() if self.annotation else None,
            "points_count": self.points_count,
            "created_at": self.created_at,
            "active": active_group == self.name,
        }


class CalibrationManager:
    """Manage calibration groups stored under configs/calibration/."""

    def __init__(self, calibration_root: str | Path | None = None) -> None:
        self._root = Path(calibration_root) if calibration_root else config.CALIBRATION_DIR
        self._state_path = self._root / _STATE_FILENAME
        self._template_xml = config.CALIBRATION_TEMPLATE_ANNOTATION
        self._ensure_ready()

    # ------------------------------------------------------------------ State

    def _ensure_ready(self) -> None:
        self._root.mkdir(parents=True, exist_ok=True)
        state = self._load_state()
        changed = False
        if not state:
            state = {"active_group": None, "globals": {}}
            changed = True

        group_dirs = [p for p in self._root.iterdir() if p.is_dir()]
        if not group_dirs:
            default_dir = self._root / "default"
            self._seed_group(default_dir)
            group_dirs = [default_dir]
            if not state.get("active_group"):
                state["active_group"] = default_dir.name
                changed = True

        if not state.get("active_group") and group_dirs:
            state["active_group"] = group_dirs[0].name
            changed = True

        if changed:
            self._write_state(state)

    def _load_state(self) -> Dict[str, Any]:
        return _read_json(self._state_path, {"active_group": None, "globals": {}})

    def _write_state(self, payload: Dict[str, Any]) -> None:
        _write_json(self._state_path, payload)

    def _seed_group(self, target_dir: Path) -> None:
        target_dir.mkdir(parents=True, exist_ok=True)
        # Copy legacy root assets into the new folder if present
        for candidate in self._root.glob("src_*"):
            if candidate.is_file():
                shutil.copy2(candidate, target_dir / candidate.name)
        # Ensure annotation XML exists
        xml_dest = target_dir / "src_IMG_Color.xml"
        if not xml_dest.exists():
            if (self._root / "src_IMG_Color.xml").exists():
                shutil.copy2(self._root / "src_IMG_Color.xml", xml_dest)
            elif self._template_xml.exists():
                shutil.copy2(self._template_xml, xml_dest)
        data_path = target_dir / _DATA_FILENAME
        if not data_path.exists():
            _write_json(
                data_path,
                {
                    "record_id": None,
                    "points": [],
                    "matrices": {
                        "pixel_to_camera": [],
                        "camera_to_machine": [],
                        "pixel_to_machine": [],
                    },
                },
            )

    # --------------------------------------------------------------- Utilities

    def _group_dir(self, name: str) -> Path:
        safe_name = _sanitize_name(name)
        return self._root / safe_name

    def _best_image_in(self, folder: Path) -> Optional[Path]:
        for name in _DEFAULT_COLOR_CANDIDATES:
            candidate = folder / name
            if candidate.exists():
                return candidate
        for candidate in folder.glob("src_*"):
            if candidate.is_file():
                return candidate
        return None

    def _annotation_in(self, folder: Path) -> Optional[Path]:
        candidate = folder / "src_IMG_Color.xml"
        return candidate if candidate.exists() else None

    def _probe_image_size(self, image_path: Optional[Path]) -> tuple[int, int]:
        if not image_path or not image_path.exists():
            return 0, 0
        try:
            import cv2  # type: ignore

            img = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
            if img is not None:
                h, w = img.shape[:2]
                return int(w), int(h)
        except Exception:
            pass
        return 0, 0

    def _load_group_data(self, folder: Path) -> Dict[str, Any]:
        return _read_json(folder / _DATA_FILENAME, {"record_id": None, "points": [], "matrices": {}})

    def _save_group_data(self, folder: Path, payload: Dict[str, Any]) -> None:
        sanitized = {
            "record_id": payload.get("record_id"),
            "points": payload.get("points") or [],
            "matrices": payload.get("matrices") or {},
        }
        _write_json(folder / _DATA_FILENAME, sanitized)

    # ----------------------------------------------------------------- Public

    def list_overview(self) -> Dict[str, Any]:
        self._ensure_ready()
        state = self._load_state()
        groups: List[CalibrationGroupOverview] = []
        for item in sorted(self._root.iterdir()):
            if not item.is_dir():
                continue
            data = self._load_group_data(item)
            color = self._best_image_in(item)
            overview = CalibrationGroupOverview(
                name=item.name,
                path=item,
                color_image=color,
                annotation=self._annotation_in(item),
                points_count=len(data.get("points") or []),
                created_at=item.stat().st_mtime,
            )
            groups.append(overview)
        return {
            "active": state.get("active_group"),
            "globals": state.get("globals", {}),
            "groups": [g.to_dict(state.get("active_group")) for g in groups],
        }

    def ensure_active_payload(self) -> Dict[str, Any]:
        """Return payload compatible with legacy /vision/calibration endpoint."""
        self._ensure_ready()
        state = self._load_state()
        active = state.get("active_group")
        folder = self._group_dir(active) if active else _best_existing_group(self._root)
        if not folder or not folder.exists():
            folder = _best_existing_group(self._root)
        loader = CalibrationSettingsLoader(calibration_root=folder or self._root)
        return loader.load()

    def load_group(self, name: str) -> Dict[str, Any]:
        self._ensure_ready()
        folder = self._group_dir(name)
        if not folder.exists():
            raise FileNotFoundError(f"Calibration group not found: {name}")
        data = self._load_group_data(folder)
        color = self._best_image_in(folder)
        annotation = self._annotation_in(folder)
        width, height = self._probe_image_size(color)
        return {
            "name": folder.name,
            "folder": str(folder),
            "record_id": data.get("record_id"),
            "points": data.get("points") or [],
            "matrices": data.get("matrices") or {},
            "image": {
                "path": color.as_uri() if color else None,
                "width": width,
                "height": height,
            },
            "annotation": annotation.as_uri() if annotation else None,
        }

    def set_active(self, name: str) -> Dict[str, Any]:
        self._ensure_ready()
        folder = self._group_dir(name)
        if not folder.exists():
            raise FileNotFoundError(f"Calibration group not found: {name}")
        state = self._load_state()
        state["active_group"] = folder.name
        self._write_state(state)
        return self.load_group(folder.name)

    def create_group(self, name: Optional[str] = None, record_id: Optional[int] = None) -> Dict[str, Any]:
        self._ensure_ready()
        requested = name or f"calib_{time.strftime('%Y%m%d_%H%M%S')}"
        folder = self._group_dir(requested)
        if folder.exists() and any(folder.iterdir()):
            raise FileExistsError(f"Calibration group already exists: {folder.name}")
        folder.mkdir(parents=True, exist_ok=True)

        # Copy current artifacts
        copied = save_data.copy_current_artifacts(folder)
        if not copied:
            log.info("No current artifacts were copied for %s; attempting legacy seed.", folder)
            self._seed_group(folder)

        # Copy annotation xml from latest existing group or template
        xml_source = None
        previous = _best_existing_group(self._root, exclude=folder.name)
        if previous and (previous / "src_IMG_Color.xml").exists():
            xml_source = previous / "src_IMG_Color.xml"
        elif (self._root / "src_IMG_Color.xml").exists():
            xml_source = self._root / "src_IMG_Color.xml"
        elif self._template_xml.exists():
            xml_source = self._template_xml
        if xml_source:
            shutil.copy2(xml_source, folder / "src_IMG_Color.xml")

        # Initialize data file
        if record_id is None:
            record_id = _latest_record_id(config.SAVE_DATA_RECORDS_DIR)
        payload = {
            "record_id": record_id,
            "points": [],
            "matrices": {
                "pixel_to_camera": [],
                "camera_to_machine": [],
                "pixel_to_machine": [],
            },
        }
        self._save_group_data(folder, payload)

        state = self._load_state()
        state["active_group"] = folder.name
        self._write_state(state)
        return self.load_group(folder.name)

    def compute_matrices(self, points: list[dict[str, Any]]) -> dict:
        pixel_cam = _affine2d(points)
        cam_mach = _affine3d(points)
        pixel_mach: list[list[float]] = []
        if pixel_cam and cam_mach:
            # Embed 2D affine into 4x4 and compose
            pixel_cam4 = [
                [pixel_cam[0][0], pixel_cam[0][1], 0.0, pixel_cam[0][2]],
                [pixel_cam[1][0], pixel_cam[1][1], 0.0, pixel_cam[1][2]],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
            try:
                import numpy as np  # type: ignore

                pc = np.asarray(pixel_cam4, dtype=float)
                cm = np.asarray(cam_mach, dtype=float)
                composed = cm @ pc
                pixel_mach = composed.tolist()
            except Exception:
                pixel_mach = []
        return {
            "pixel_to_camera": pixel_cam,
            "camera_to_machine": cam_mach,
            "pixel_to_machine": pixel_mach,
        }

    def delete_group(self, name: str) -> Dict[str, Any]:
        self._ensure_ready()
        folder = self._group_dir(name)
        if not folder.exists():
            raise FileNotFoundError(f"Calibration group not found: {name}")
        shutil.rmtree(folder)
        state = self._load_state()
        if state.get("active_group") == folder.name:
            replacement = _best_existing_group(self._root)
            state["active_group"] = replacement.name if replacement else None
        self._write_state(state)
        return self.list_overview()

    def rename_group(self, old_name: str, new_name: str) -> Dict[str, Any]:
        """Rename an existing calibration group folder."""
        self._ensure_ready()
        src_dir = self._group_dir(old_name)
        if not src_dir.exists():
            raise FileNotFoundError(f"Calibration group not found: {old_name}")
        # normalise new name and avoid collisions
        dst_dir = self._group_dir(new_name)
        if dst_dir.exists():
            raise FileExistsError(f"Calibration group already exists: {dst_dir.name}")
        dst_dir.parent.mkdir(parents=True, exist_ok=True)
        src_dir.rename(dst_dir)

        state = self._load_state()
        if state.get("active_group") == src_dir.name:
            state["active_group"] = dst_dir.name
        self._write_state(state)
        return self.load_group(dst_dir.name)

    def save_group_data(self, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_ready()
        folder = self._group_dir(name)
        if not folder.exists():
            raise FileNotFoundError(f"Calibration group not found: {name}")
        self._save_group_data(folder, payload)
        return self.load_group(folder.name)

    def import_image(self, name: str, source_path: Optional[str] = None, use_current: bool = False) -> Dict[str, Any]:
        self._ensure_ready()
        folder = self._group_dir(name)
        if not folder.exists():
            raise FileNotFoundError(f"Calibration group not found: {name}")

        copied: List[Path] = []
        if use_current:
            copied = save_data.copy_current_artifacts(folder)
        elif source_path:
            src = Path(source_path)
            if not src.exists():
                raise FileNotFoundError(f"Image not found: {source_path}")
            dest = folder / src.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            copied = [dest]

        if not copied:
            log.warning("No images were imported for calibration group %s", name)
        return self.load_group(folder.name)


__all__ = ["CalibrationManager"]
