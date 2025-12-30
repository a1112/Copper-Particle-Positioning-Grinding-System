from __future__ import annotations

from dataclasses import dataclass, field, asdict
import json
from pathlib import Path
from typing import Dict, Iterable

from app import config as APP_CONFIG


CALIBRATION_ROOT = APP_CONFIG.CALIBRATION_DIR
CALIBRATION_STATE_PATH = APP_CONFIG.CALIBRATION_STATE_PATH
CALIBRATION_TEMPLATE_ANNOTATION = APP_CONFIG.CALIBRATION_TEMPLATE_ANNOTATION
CALIBRATION_ANNOTATION_NAME = "src_IMG_Color.xml"


def resolve_default_fixture_annotation() -> Path | None:
    """从 calibration.json 中解析当前标定组并返回默认的夹具标注文件路径。

    优先顺序：
    1. configs/calibration/calibration.json 指定的 active_group 目录下的 src_IMG_Color.xml
    2. 旧版平铺路径 configs/calibration/src_IMG_Color.xml
    3. 模板路径 configs/template/src_IMG_Color.xml
    """
    try:
        if CALIBRATION_STATE_PATH.exists():
            with CALIBRATION_STATE_PATH.open("r", encoding="utf-8") as fh:
                state = json.load(fh)
            active_group = state.get("active_group")
            if active_group:
                candidate = CALIBRATION_ROOT / active_group / CALIBRATION_ANNOTATION_NAME
                if candidate.exists():
                    return candidate
    except Exception:
        # 任意解析错误时退回到旧路径 / 模板路径
        pass

    legacy = CALIBRATION_ROOT / CALIBRATION_ANNOTATION_NAME
    if legacy.exists():
        return legacy

    if CALIBRATION_TEMPLATE_ANNOTATION.exists():
        return CALIBRATION_TEMPLATE_ANNOTATION

    return None


@dataclass(slots=True)
class TaskConfig:
    """任务 1 管线使用的配置项（单位默认为毫米）。"""

    source_dir: Path = APP_CONFIG.SAVE_DATA_CURRENT_DIR
    output_dir: Path = APP_CONFIG.SAVE_DATA_CURRENT_DIR / "alg_task1"
    grid_step: int = 1
    valid_epsilon: float = 1e-3
    board_residual_threshold: float = 0.35
    board_close_threshold: float = 0.75
    particle_height_threshold: float = 0.6
    reference_plane_z: float = 1800.0
    particle_merge_distance_mm: float = 1.5
    particle_min_area_mm2: float = 4.0
    fixture_height_threshold: float = 4.0
    fixture_min_area_mm2: float = 10.0
    fixture_edge_band_mm: float = 25.0
    finish_allowance: float = 1.5
    tool_diameter: float = 80.0
    tool_safety_margin: float = 1.5
    stepover_ratio: float = 0.55
    clearance_height: float = 5.0
    rapid_height: float = 3.0
    feed_rates_mm_min: Dict[str, float] = field(
        default_factory=lambda: {
            "sparse": 180.0,
            "normal": 140.0,
            "dense": 90.0,
        }
    )
    travel_speed_mm_min: float = 500.0
    cut_depth_sparse: float = 0.6
    cut_depth_normal: float = 0.45
    cut_depth_dense: float = 0.3
    min_segment_length_mm: float = 1.5
    visualization_size: int = 1024
    step_simulation: bool = True
    simulate_limit_segments: int = 200
    save_height_map: bool = True
    board_base_blur_kernel: int = 51
    particle_keep_height: float = 2.0
    fixture_annotation: Path | None = None
    height_display_max: float = 100.0
    fixture_merge_particle_px: int = 20
    fixture_near_distance_px: int = 15
    board_mask_reference_height: float = 1800.0

    def feed_for_density(self, density: float) -> float:
        """根据颗粒密度分类返回进给速度。"""
        if density < 0.25:
            return self.feed_rates_mm_min["sparse"]
        if density < 0.55:
            return self.feed_rates_mm_min["normal"]
        return self.feed_rates_mm_min["dense"]

    def cut_depth_for_density(self, density: float) -> float:
        """根据颗粒密度分类返回单层切削深度。"""
        if density < 0.25:
            return self.cut_depth_sparse
        if density < 0.55:
            return self.cut_depth_normal
        return self.cut_depth_dense

    def to_dict(self) -> Dict[str, object]:
        """转换为便于序列化的字典，路径字段改为字符串。"""
        payload = asdict(self)
        payload["source_dir"] = str(self.source_dir)
        payload["output_dir"] = str(self.output_dir)
        payload["fixture_annotation"] = str(self.fixture_annotation) if self.fixture_annotation else None
        payload["board_mask_reference_height"] = self.board_mask_reference_height
        return payload

    @classmethod
    def from_args(cls, args: Iterable[str] | None = None) -> TaskConfig:
        """从命令行参数构建 TaskConfig，未提供时使用默认值。"""
        from argparse import ArgumentParser

        defaults = cls()
        parser = ArgumentParser(description="Structured-light copper board particle removal task.")
        parser.add_argument(
            "--source-dir", type=Path, default=defaults.source_dir, help="Capture folder with point clouds."
        )
        parser.add_argument("--output-dir", type=Path, default=defaults.output_dir, help="Directory to write outputs.")
        parser.add_argument(
            "--grid-step", type=int, default=defaults.grid_step, help="Downsampling step for the point cloud."
        )
        parser.add_argument(
            "--particle-height",
            type=float,
            default=defaults.particle_height_threshold,
            help="Minimum protrusion (mm) above the base plane to classify as a particle.",
        )
        parser.add_argument(
            "--tool-diameter",
            type=float,
            default=defaults.tool_diameter,
            help="Tool diameter used for path planning (mm).",
        )
        parser.add_argument(
            "--finish-allowance",
            type=float,
            default=defaults.finish_allowance,
            help="Residue height to leave above the base plane after machining (mm).",
        )
        parser.add_argument(
            "--fixture-annotation",
            type=Path,
            default=None,
            help="LabelImg XML annotating fixture regions.",
        )
        parser.add_argument(
            "--particle-keep-height",
            type=float,
            default=defaults.particle_keep_height,
            help="Allowance height (mm) to retain above the base plane when marking particles.",
        )
        parser.add_argument(
            "--reference-plane-z",
            type=float,
            default=defaults.reference_plane_z,
            help="Reference plane Z (mm) used to compute protrusion heights.",
        )
        parser.add_argument(
            "--height-display-max",
            type=float,
            default=defaults.height_display_max,
            help="Maximum height (mm) mapped to the top of HSV colour scale.",
        )
        parser.add_argument(
            "--fixture-merge-px",
            type=int,
            default=defaults.fixture_merge_particle_px,
            help="Merge particle components (<= this pixel count) into fixtures when touching fixture mask.",
        )
        parser.add_argument(
            "--fixture-near-px",
            type=int,
            default=defaults.fixture_near_distance_px,
            help="Distance in pixels to treat a particle as 'near' fixtures for removal/merging.",
        )
        parser.add_argument(
            "--board-mask-ref-height",
            type=float,
            default=defaults.board_mask_reference_height,
            help="Reference height (mm) used when generating board_mask residual map (value -> ref - z).",
        )
        options = parser.parse_args(args=args)
        config = defaults
        config.source_dir = options.source_dir
        config.output_dir = options.output_dir
        config.grid_step = max(1, options.grid_step)
        config.particle_height_threshold = options.particle_height
        config.tool_diameter = options.tool_diameter
        config.finish_allowance = max(0.0, options.finish_allowance)
        config.reference_plane_z = options.reference_plane_z
        config.height_display_max = max(1e-3, options.height_display_max)
        config.fixture_annotation = options.fixture_annotation or resolve_default_fixture_annotation()
        config.particle_keep_height = max(0.0, options.particle_keep_height)
        config.fixture_merge_particle_px = max(1, options.fixture_merge_px)
        config.fixture_near_distance_px = max(0, options.fixture_near_px)
        config.board_mask_reference_height = float(options.board_mask_ref_height)
        return config
