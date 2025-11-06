from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np

from .config import TaskConfig
from .data_io import POINT_CLOUD_FILES
from .models import PipelineResult
from .pipeline import run_pipeline

DEFAULT_DIFF_NAME = "rts_ImageSubZ1.tif"


def _expand_mask(mask: np.ndarray, step: int, target_shape: Tuple[int, int]) -> np.ndarray:
    """将降采样掩膜按指定步长扩展到全分辨率。"""
    expanded = np.repeat(mask, step, axis=0)
    expanded = np.repeat(expanded, step, axis=1)
    return expanded[: target_shape[0], : target_shape[1]]


def _build_particle_mask(result: PipelineResult) -> np.ndarray:
    """合并所有颗粒簇的像素掩膜。"""
    combined = np.zeros_like(result.cloud.valid_mask, dtype=bool)
    for particle in result.particles:
        r0, r1, c0, c1 = particle.bbox
        combined[r0:r1, c0:c1] |= particle.mask
    return combined


def generate_rts_overlay(
    config: TaskConfig,
    *,
    diff_filename: str = DEFAULT_DIFF_NAME,
    output_path: Optional[Path] = None,
    result: Optional[PipelineResult] = None,
) -> Path:
    """生成颗粒掩膜叠加在差分高度图上的调试图。"""
    diff_path = config.source_dir / diff_filename
    diff_image = cv2.imread(str(diff_path), cv2.IMREAD_UNCHANGED)
    if diff_image is None:
        raise FileNotFoundError(f"Unable to read reference image: {diff_path}")

    if result is None:
        result, _ = run_pipeline(config, build_visuals=False)

    mask_down = _build_particle_mask(result)
    step = max(1, result.cloud.step)
    mask_full = _expand_mask(mask_down, step, diff_image.shape[:2])

    norm = cv2.normalize(diff_image, None, 0, 255, cv2.NORM_MINMAX)
    norm_u8 = norm.astype(np.uint8)
    base_color = cv2.applyColorMap(norm_u8, cv2.COLORMAP_VIRIDIS)
    overlay = base_color.copy()
    overlay[mask_full] = (0, 0, 255)

    if result.particles:
        top_particle = max(result.particles, key=lambda item: item.max_height)
        highlight_down = np.zeros_like(mask_down, dtype=bool)
        r0, r1, c0, c1 = top_particle.bbox
        highlight_down[r0:r1, c0:c1] = top_particle.mask
        highlight_full = _expand_mask(highlight_down, step, diff_image.shape[:2])
        overlay[highlight_full] = (0, 255, 255)

    mask_uint8 = (mask_full.astype(np.uint8)) * 255
    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours, -1, (255, 0, 0), 1)

    if output_path is None:
        output_path = config.output_dir / "rts_overlay.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), overlay)
    return output_path


def generate_board_outline(
    config: TaskConfig,
    *,
    output_path: Optional[Path] = None,
    result: Optional[PipelineResult] = None,
    z_range: Optional[Tuple[float, float]] = None,
) -> Path:
    """绘制板面主区域及夹具分布，用于人工校验。"""
    if result is None:
        result, _ = run_pipeline(config, build_visuals=False)

    mask = result.board_main_region_full
    fixture_mask = result.fixture_mask_full
    h, w = mask.shape

    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    canvas[mask] = (180, 180, 180)
    canvas[fixture_mask] = (0, 0, 255)

    contours, _ = cv2.findContours((mask.astype(np.uint8)) * 255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise RuntimeError("Unable to extract board contour from board_main_region.")

    for contour in contours:
        cv2.drawContours(canvas, [contour], -1, (0, 255, 0), thickness=2)

    if output_path is None:
        output_path = config.output_dir / "board_outline.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), canvas)
    return output_path
