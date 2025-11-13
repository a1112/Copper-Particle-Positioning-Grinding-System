from __future__ import annotations

import json
import logging
import shutil
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

import cv2
import numpy as np

from app import config
from app.vision.task1.config import TaskConfig
from app.vision.task1.data_io import POINT_CLOUD_FILES
from app.vision.task1.export import export_summary, export_visuals
from app.vision.task1.pipeline import run_pipeline

LOG = logging.getLogger(__name__)

TEXTURE_IMAGE_NAME = "src_IMG_Texture_8Bit.png"
COLOR_IMAGE_NAME = "src_IMG_Color.png"

_SIM_SAMPLE_DIR = config.TEST_DATA_DIR / "images"
_DEFAULT_SAVE_DIR = config.SAVE_DATA_CURRENT_DIR
_EXTRA_TARGETS: Sequence[str] = (TEXTURE_IMAGE_NAME, COLOR_IMAGE_NAME)

_SIM_PATTERN_MAP: Dict[str, Sequence[str]] = {
    POINT_CLOUD_FILES["x"]: ("*PointCloud_X*.tif", "*X1.tif"),
    POINT_CLOUD_FILES["y"]: ("*PointCloud_Y*.tif", "*Y1.tif"),
    POINT_CLOUD_FILES["z"]: ("*PointCloud_Z*.tif", "*Z1.tif"),
    COLOR_IMAGE_NAME: ("*_IMG_Color.png", "*_IMG_Color.tif"),
    TEXTURE_IMAGE_NAME: ("*_IMG_Texture_8Bit.png", "*_ImageZ1ZeroReal.tif"),
}

_PARAMETER_SPEC: Sequence[Dict[str, Any]] = [
    {"key": "grid_step", "label": "点云下采样步长", "type": "int", "min": 1, "max": 8, "step": 1},
    {"key": "particle_height_threshold", "label": "颗粒高度阈值 (mm)", "type": "float", "min": 0.1, "max": 5.0, "step": 0.05},
    {"key": "fixture_height_threshold", "label": "夹具高度阈值 (mm)", "type": "float", "min": 1.0, "max": 20.0, "step": 0.1},
    {"key": "fixture_min_area_mm2", "label": "夹具最小面积 (mm²)", "type": "float", "min": 1.0, "max": 500.0, "step": 1.0},
    {"key": "particle_min_area_mm2", "label": "颗粒最小面积 (mm²)", "type": "float", "min": 0.5, "max": 200.0, "step": 0.5},
    {"key": "particle_merge_distance_mm", "label": "颗粒合并距离 (mm)", "type": "float", "min": 0.1, "max": 10.0, "step": 0.1},
    {"key": "fixture_edge_band_mm", "label": "夹具边带宽度 (mm)", "type": "float", "min": 1.0, "max": 50.0, "step": 0.5},
    {"key": "finish_allowance", "label": "残留余量 (mm)", "type": "float", "min": 0.1, "max": 5.0, "step": 0.05},
    {"key": "tool_diameter", "label": "刀具直径 (mm)", "type": "float", "min": 5.0, "max": 200.0, "step": 1.0},
    {"key": "tool_safety_margin", "label": "刀具安全裕度 (mm)", "type": "float", "min": 0.1, "max": 10.0, "step": 0.1},
    {"key": "stepover_ratio", "label": "步距系数", "type": "float", "min": 0.1, "max": 1.0, "step": 0.01},
    {"key": "clearance_height", "label": "安全高度 (mm)", "type": "float", "min": 1.0, "max": 30.0, "step": 0.5},
]


class Task1CaptureError(RuntimeError):
    """Raised when a capture profile fails."""


class Task1RunError(RuntimeError):
    """Raised when the pipeline cannot be executed."""


@dataclass(slots=True)
class CaptureReport:
    profile: str
    source_dir: Path
    files: Sequence[Path]
    message: str


@dataclass(slots=True)
class Task1RunResult:
    source_dir: Path
    output_dir: Path
    summary_path: Path
    metrics: Dict[str, Any]
    visuals: Dict[str, Sequence[Path]]
    capture: Optional[CaptureReport] = None


@dataclass(slots=True)
class Task1RunOptions:
    mode: str = "capture"
    folder: Optional[str] = None
    camera_profile: Optional[str] = None
    camera_serial: Optional[str] = None
    overrides: Mapping[str, Any] = field(default_factory=dict)
    build_visuals: bool = True


class CameraCaptureService:
    """Prepare SaveData/current by copying samples or triggering hardware capture."""

    def __init__(self, *, save_dir: Path | None = None, sample_dir: Path | None = None) -> None:
        self._save_dir = (save_dir or _DEFAULT_SAVE_DIR).expanduser()
        self._sample_dir = (sample_dir or _SIM_SAMPLE_DIR).expanduser()
        if not self._ensure_dir(self._save_dir):
            fallback = (Path("SaveData") / "current").expanduser()
            fallback.mkdir(parents=True, exist_ok=True)
            self._save_dir = fallback
        self.default_profile = "sim"

    # Public API ---------------------------------------------------------

    def profile_catalog(self) -> Sequence[Dict[str, Any]]:
        """Return metadata for available camera profiles."""
        catalog = [
            {
                "id": "sim",
                "label": "示例 3D 相机 (TestData)",
                "description": "使用仓库内置样例点云覆盖 SaveData/current。",
                "kind": "simulated",
                "available": True,
            }
        ]
        catalog.append(
            {
                "id": "mecheye",
                "label": "Mech-Eye 结构光相机",
                "description": "需要安装 MechEyeAPI，并在本地连接设备。",
                "kind": "hardware",
                "available": self._mecheye_available(),
            }
        )
        return catalog

    def capture(self, profile: Optional[str] = None, *, serial: Optional[str] = None) -> CaptureReport:
        """Execute capture workflow for the selected profile."""
        profile_id = (profile or self.default_profile).strip().lower()
        self._clean_targets()
        if profile_id == "sim":
            files = self._copy_simulated_assets()
            message = "已从 TestData/images 复制示例点云。"
        elif profile_id == "mecheye":
            files = self._capture_mecheye(serial=serial)
            message = "Mech-Eye 相机采集完成。"
        else:
            raise Task1CaptureError(f"未知 3D 相机配置: {profile_id}")
        return CaptureReport(profile=profile_id, source_dir=self._save_dir, files=files, message=message)

    # Internal helpers ---------------------------------------------------

    def _clean_targets(self) -> None:
        for filename in (*POINT_CLOUD_FILES.values(), *_EXTRA_TARGETS):
            try:
                target = self._save_dir / filename
                if target.exists():
                    target.unlink()
            except Exception as exc:  # pragma: no cover - defensive logging
                LOG.warning("无法清理旧文件 %s: %s", target, exc)

    def _copy_simulated_assets(self) -> list[Path]:
        if not self._sample_dir.exists():
            raise Task1CaptureError(f"示例目录缺失: {self._sample_dir}")
        copied: list[Path] = []
        for target, patterns in _SIM_PATTERN_MAP.items():
            source = self._find_first(patterns)
            destination = self._save_dir / target
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied.append(destination)
        return copied

    def _find_first(self, patterns: Sequence[str]) -> Path:
        for pattern in patterns:
            matches = sorted(self._sample_dir.glob(pattern))
            if matches:
                return matches[0]
        raise Task1CaptureError(f"示例目录 {self._sample_dir} 中缺少 {patterns} 对应的文件。")

    def _capture_mecheye(self, *, serial: Optional[str]) -> list[Path]:
        try:
            from app.vision.mecheye_cap import MechEyeCapture
        except ImportError as exc:  # pragma: no cover - optional path
            raise Task1CaptureError("未安装 MechEyeAPI，无法执行相机采集。") from exc

        capture = MechEyeCapture(output_dir=self._save_dir)
        try:
            capture.connect(serial=serial)
            result = capture.capture_once()
        except Exception as exc:  # pragma: no cover - hardware path
            raise Task1CaptureError(f"相机采集失败: {exc}") from exc

        if result.point_map is None:
            raise Task1CaptureError("硬件未返回 point_map，无法生成 PointCloud 切片。")
        files = self._write_point_map_planes(result.point_map)
        if result.color_array is not None:
            files.extend(self._write_color_frames(result.color_array))
        elif result.color_path and result.color_path.exists():
            destination = self._save_dir / COLOR_IMAGE_NAME
            shutil.copy2(result.color_path, destination)
            files.append(destination)
        if result.depth_array is not None:
            files.extend(self._write_texture_frame(result.depth_array))
        elif result.depth_path and result.depth_path.exists():
            destination = self._save_dir / TEXTURE_IMAGE_NAME
            shutil.copy2(result.depth_path, destination)
            files.append(destination)
        return files

    def _ensure_dir(self, path: Path) -> bool:
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as exc:
            LOG.warning("无法创建保存目录 %s: %s", path, exc)
            return False

    def _write_point_map_planes(self, point_map: np.ndarray) -> list[Path]:
        if point_map.ndim != 3 or point_map.shape[2] < 3:
            raise Task1CaptureError("point_map 需为 HxWx3 数组。")
        outputs: list[Path] = []
        for axis_key, array in zip(("x", "y", "z"), np.moveaxis(point_map, -1, 0)):
            filename = POINT_CLOUD_FILES[axis_key]
            target = self._save_dir / filename
            data = np.nan_to_num(array, nan=0.0).astype(np.float32)
            cv2.imwrite(str(target), data)
            outputs.append(target)
        return outputs

    def _write_color_frames(self, color_array: np.ndarray) -> list[Path]:
        if color_array.ndim < 2:
            raise Task1CaptureError("彩色图像维度异常。")
        rgb = np.nan_to_num(color_array, nan=0.0)
        if rgb.dtype != np.uint8:
            rgb = np.clip(rgb, 0, 255).astype(np.uint8)
        if rgb.ndim == 2:
            rgb = np.stack([rgb, rgb, rgb], axis=-1)
        color_img = rgb[:, :, :3]
        color_path = self._save_dir / COLOR_IMAGE_NAME
        cv2.imwrite(str(color_path), color_img[:, :, ::-1])
        gray = cv2.cvtColor(color_img, cv2.COLOR_RGB2GRAY)
        texture_path = self._save_dir / TEXTURE_IMAGE_NAME
        cv2.imwrite(str(texture_path), gray)
        return [color_path, texture_path]

    def _write_texture_frame(self, depth_array: np.ndarray) -> list[Path]:
        texture_path = self._save_dir / TEXTURE_IMAGE_NAME
        data = np.nan_to_num(depth_array, nan=0.0)
        # Normalize depth map to 0-255 for visualization
        min_val = float(np.min(data))
        max_val = float(np.max(data))
        denom = max(max_val - min_val, 1e-6)
        norm = ((data - min_val) / denom) * 255.0
        cv2.imwrite(str(texture_path), norm.astype(np.uint8))
        return [texture_path]

    def _mecheye_available(self) -> bool:
        try:
            import importlib

            importlib.import_module("MechEye")  # type: ignore[import]
            return True
        except Exception:
            return False


class Task1Runner:
    """High-level facade to run the task1 pipeline from capture/folder sources."""

    def __init__(self, *, save_dir: Path | None = None, sample_dir: Path | None = None) -> None:
        self._capture_service = CameraCaptureService(save_dir=save_dir, sample_dir=sample_dir)
        self._lock = threading.Lock()

    # Metadata -----------------------------------------------------------

    def camera_profiles(self) -> Sequence[Dict[str, Any]]:
        return self._capture_service.profile_catalog()

    def parameter_schema(self) -> Sequence[Dict[str, Any]]:
        defaults = TaskConfig()
        schema = []
        for item in _PARAMETER_SPEC:
            enriched = dict(item)
            enriched["default"] = getattr(defaults, item["key"])
            schema.append(enriched)
        return schema

    # Execution ----------------------------------------------------------

    def run(self, options: Task1RunOptions) -> Task1RunResult:
        with self._lock:
            capture_report: Optional[CaptureReport] = None
            if options.mode == "folder":
                source_dir = self._resolve_folder(options.folder)
            else:
                capture_report = self._capture_service.capture(
                    profile=options.camera_profile,
                    serial=options.camera_serial,
                )
                source_dir = capture_report.source_dir
            config_obj = self._build_config(source_dir, options.overrides)
            result, visuals = run_pipeline(config_obj, build_visuals=options.build_visuals)
            summary_path = export_summary(result, config_obj, Path(config_obj.output_dir) / "task1_result.json")
            written_visuals = export_visuals(Path(config_obj.output_dir), visuals if options.build_visuals else {})
            metrics = self._summarise_metrics(result, summary_path)
            return Task1RunResult(
                source_dir=source_dir,
                output_dir=Path(config_obj.output_dir),
                summary_path=summary_path,
                metrics=metrics,
                visuals=written_visuals,
                capture=capture_report,
            )

    # Helpers ------------------------------------------------------------

    def _resolve_folder(self, folder: Optional[str]) -> Path:
        if not folder:
            raise Task1RunError("未提供数据文件夹路径。")
        path = Path(folder).expanduser()
        if not path.exists():
            raise Task1RunError(f"数据文件夹不存在: {path}")
        missing = [fname for fname in POINT_CLOUD_FILES.values() if not (path / fname).exists()]
        if missing:
            raise Task1RunError(f"数据文件夹缺少必要文件: {missing}")
        return path

    def _build_config(self, source_dir: Path, overrides: Mapping[str, Any]) -> TaskConfig:
        cfg = TaskConfig()
        cfg.source_dir = source_dir
        cfg.output_dir = source_dir / "alg_task1"
        cfg.output_dir.mkdir(parents=True, exist_ok=True)
        self._apply_overrides(cfg, overrides)
        return cfg

    def _apply_overrides(self, cfg: TaskConfig, overrides: Mapping[str, Any]) -> None:
        if not overrides:
            return
        for item in _PARAMETER_SPEC:
            key = item["key"]
            if key not in overrides:
                continue
            raw_value = overrides[key]
            if raw_value is None:
                continue
            try:
                if item["type"] == "int":
                    value = int(raw_value)
                else:
                    value = float(raw_value)
            except (TypeError, ValueError) as exc:
                raise Task1RunError(f"参数 {key} 无法转为 {item['type']}") from exc
            min_val = item.get("min")
            max_val = item.get("max")
            if min_val is not None:
                value = max(min_val, value)
            if max_val is not None:
                value = min(max_val, value)
            if item["type"] == "int":
                value = int(value)
            setattr(cfg, key, value)

    def _summarise_metrics(self, result, summary_path: Path) -> Dict[str, Any]:
        metrics = {
            "board_height": float(result.board_height),
            "plane_rms_error": float(result.plane.rms_error),
            "fixture_count": len(result.fixtures),
            "particle_count": len(result.particles),
            "toolpath_segments": len(result.toolpaths.segments),
        }
        try:
            with summary_path.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
            metrics["summary"] = payload
        except Exception as exc:  # pragma: no cover - best effort
            LOG.warning("无法解析 task1_result.json (%s): %s", summary_path, exc)
        return metrics


__all__ = [
    "CameraCaptureService",
    "CaptureReport",
    "Task1Runner",
    "Task1RunError",
    "Task1RunOptions",
    "Task1RunResult",
]
