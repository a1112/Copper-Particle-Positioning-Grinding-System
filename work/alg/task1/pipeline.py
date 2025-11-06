from __future__ import annotations

from typing import Dict, Tuple

import cv2
import numpy as np

from .board_detection import detect_board_and_fixtures
from .config import TaskConfig
from .data_io import load_downsampled_cloud
from .models import PipelineResult, PlaneModel
from .path_planner import plan_toolpaths
from .segmentation import detect_fixtures, detect_particles
from .visualization import generate_visualizations


def _downsample(array: np.ndarray, step: int) -> np.ndarray:
    """按步长对数组进行整齐下采样。"""
    return array[::step, ::step]


def _merge_particles_into_fixtures(
    particles,
    fixture_mask: np.ndarray,
    max_pixels: int,
    near_px: int,
):
    """将过小且靠近夹具的颗粒并入夹具掩膜，避免后续加工。"""
    keep = []
    updated_mask = fixture_mask.copy()
    near_px = max(0, int(near_px))
    kernel_size = 2 * near_px + 1 if near_px > 0 else 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    for cluster in particles:
        pixel_count = int(cluster.mask.sum())
        if pixel_count <= max_pixels:
            mask = np.zeros_like(updated_mask, dtype=bool)
            r0, r1, c0, c1 = cluster.bbox
            mask[r0:r1, c0:c1] = cluster.mask
            # Treat as 'near' by dilating fixture mask and checking intersection
            dilated_fixture = cv2.dilate(updated_mask.astype(np.uint8), kernel, iterations=1).astype(bool)
            if (mask & dilated_fixture).any():
                updated_mask |= mask
                continue
        keep.append(cluster)
    return keep, updated_mask


def run_pipeline(config: TaskConfig, build_visuals: bool = True) -> Tuple[PipelineResult, Dict[str, object]]:
    """贯穿加载、检测、规划、可视化的核心管线。"""
    cloud = load_downsampled_cloud(config)
    detection = detect_board_and_fixtures(config, cloud)

    step = max(1, cloud.step)
    z_down = _downsample(detection.z_image, step)
    base_down = _downsample(detection.base_height_map, step)
    board_residual_full = detection.board_residual_full
    valid_z_down = z_down > 0
    board_mask_down = detection.board_mask_down & cloud.valid_mask & valid_z_down
    fixture_mask_down = detection.fixture_mask_down & cloud.valid_mask & valid_z_down

    residual_map = base_down - z_down
    residual_map = np.nan_to_num(residual_map, nan=0.0)
    residual_map[~valid_z_down] = 0.0

    board_height_values = base_down[board_mask_down]
    board_height = float(np.median(board_height_values)) if board_height_values.size else float(np.nanmedian(base_down))

    fixtures, detected_fixture_mask = detect_fixtures(
        cloud,
        residual_map,
        board_mask_down,
        config,
        predefined_mask=fixture_mask_down,
        bounding_boxes=detection.bounding_boxes,
    )
    fixture_mask = fixture_mask_down | detected_fixture_mask

    particles = detect_particles(
        cloud,
        residual_map,
        board_mask_down,
        fixture_mask,
        config,
    )

    if particles:
        particles, fixture_mask = _merge_particles_into_fixtures(
            particles,
            fixture_mask,
            config.fixture_merge_particle_px,
            config.fixture_near_distance_px,
        )

    toolpaths = plan_toolpaths(
        cloud=cloud,
        base_map=base_down,
        board_height=board_height,
        particles=particles,
        fixture_mask=fixture_mask,
        config=config,
    )

    plane = PlaneModel(
        normal=np.array([0.0, 0.0, 1.0], dtype=np.float32),
        offset=-board_height,
        rms_error=0.0,
        inlier_ratio=1.0,
    )

    result = PipelineResult(
        cloud=cloud,
        plane=plane,
        board_mask=board_mask_down,
        residual_map=residual_map,
        board_height=board_height,
        board_mask_full=detection.board_mask_full,
        board_main_region_full=detection.board_main_region_full,
        board_residual_full=board_residual_full,
        fixture_mask_full=detection.fixture_mask_full,
        base_height_map=detection.base_height_map,
        z_image_full=detection.z_image,
        fixture_boxes=detection.bounding_boxes,
        fixtures=fixtures,
        particles=particles,
        toolpaths=toolpaths,
    )
    visuals = generate_visualizations(result, config) if build_visuals else {}
    return result, visuals
