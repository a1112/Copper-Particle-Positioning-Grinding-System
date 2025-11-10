from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

import cv2
import numpy as np

from .config import TaskConfig
from .models import DownsampledCloud, Fixture, ParticleCluster, PlaneModel
from .annotations import BoundingBox


def _close_mask(mask: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """对掩膜执行闭运算以填补小孔。"""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return (closed > 0).astype(np.uint8)


def compute_board_mask(cloud: DownsampledCloud, plane: PlaneModel, config: TaskConfig) -> np.ndarray:
    """通过平面残差与形态学滤波获得板面掩膜。"""
    residual = cloud.residual(plane)
    board_mask = (np.abs(residual) <= config.board_close_threshold) & cloud.valid_mask
    refined = _close_mask(board_mask.astype(np.uint8), kernel_size=7)
    return refined.astype(bool)


def _edge_band(board_mask: np.ndarray, spacing: float, edge_band_mm: float) -> np.ndarray:
    """根据距离变换得到板面边缘带区域。"""
    board_uint8 = board_mask.astype(np.uint8)
    dist_pixels = cv2.distanceTransform(board_uint8, cv2.DIST_L2, 3)
    distances_mm = dist_pixels * spacing
    return distances_mm <= edge_band_mm


def _extract_components(mask: np.ndarray) -> Tuple[int, np.ndarray]:
    """对掩膜执行连通域分析，返回标签数量及标签图。"""
    mask_uint8 = (mask.astype(np.uint8)) * 255
    num_labels, labels = cv2.connectedComponents(mask_uint8)
    return num_labels, labels


def detect_fixtures(
    cloud: DownsampledCloud,
    residual: np.ndarray,
    board_mask: np.ndarray,
    config: TaskConfig,
    predefined_mask: np.ndarray | None = None,
    bounding_boxes: Sequence[BoundingBox] | None = None,
) -> Tuple[List[Fixture], np.ndarray]:
    """识别夹具区域，并返回夹具对象列表及合并后的掩膜。"""
    if predefined_mask is not None and bounding_boxes:
        return _fixtures_from_boxes(
            cloud=cloud,
            residual=residual,
            board_mask=board_mask,
            mask=predefined_mask,
            boxes=bounding_boxes,
            config=config,
        )
    pixel_area = cloud.spacing_x * cloud.spacing_y
    spacing_min = min(cloud.spacing_x, cloud.spacing_y)

    if predefined_mask is not None:
        candidate_mask = predefined_mask.copy()
    else:
        candidate_mask = (residual >= config.fixture_height_threshold) & board_mask
        edge_mask = _edge_band(board_mask, spacing_min, config.fixture_edge_band_mm)
        candidate_mask &= edge_mask
        candidate_mask = _close_mask(candidate_mask.astype(np.uint8), kernel_size=5).astype(bool)

    fixtures: List[Fixture] = []
    fixture_mask = np.zeros_like(candidate_mask, dtype=bool)
    num_labels, labels = _extract_components(candidate_mask)
    next_id = 1

    for label in range(1, num_labels):
        component = labels == label
        area_pixels = int(component.sum())
        if area_pixels == 0:
            continue
        area_mm2 = area_pixels * pixel_area
        if area_mm2 < config.fixture_min_area_mm2:
            continue
        rows, cols = np.nonzero(component)
        r0, r1 = rows.min(), rows.max() + 1
        c0, c1 = cols.min(), cols.max() + 1
        submask = component[r0:r1, c0:c1]
        xs = cloud.xs[component]
        ys = cloud.ys[component]
        centroid_x = float(xs.mean())
        centroid_y = float(ys.mean())
        max_height = float(residual[component].max())
        radius = float(max(np.sqrt(area_mm2 / np.pi), config.tool_diameter * 0.5))
        if bounding_boxes:
            box = bounding_boxes[min(next_id - 1, len(bounding_boxes) - 1)]
            width_mm = float(
                np.abs(cloud.xs[r0:r1, c0:c1].max() - cloud.xs[r0:r1, c0:c1].min())
            )
            radius = max(radius, width_mm * 0.5)
        fixtures.append(
            Fixture(
                id=next_id,
                centroid_xy=(centroid_x, centroid_y),
                max_height=max_height,
                area_mm2=area_mm2,
                radius_mm=radius + config.tool_safety_margin,
                bbox=(r0, r1, c0, c1),
                mask=submask.copy(),
            )
        )
        fixture_mask |= component
        next_id += 1
    return fixtures, fixture_mask


def detect_particles(
    cloud: DownsampledCloud,
    residual: np.ndarray,
    board_mask: np.ndarray,
    fixture_mask: np.ndarray,
    config: TaskConfig,
) -> List[ParticleCluster]:
    """检测板面上显著高于基面的颗粒聚类。"""
    pixel_area = cloud.spacing_x * cloud.spacing_y
    candidate = (residual >= config.particle_keep_height) & board_mask
    candidate &= ~fixture_mask

    candidate_uint8 = _close_mask(candidate.astype(np.uint8), kernel_size=3)
    num_labels, labels = _extract_components(candidate_uint8.astype(bool))
    particles: List[ParticleCluster] = []
    next_id = 1

    for label in range(1, num_labels):
        component = labels == label
        area_pixels = int(component.sum())
        if area_pixels == 0:
            continue
        area_mm2 = area_pixels * pixel_area
        if area_mm2 < config.particle_min_area_mm2:
            continue
        rows, cols = np.nonzero(component)
        r0, r1 = rows.min(), rows.max() + 1
        c0, c1 = cols.min(), cols.max() + 1
        submask = component[r0:r1, c0:c1]
        xs = cloud.xs[component]
        ys = cloud.ys[component]
        centroid_x = float(xs.mean())
        centroid_y = float(ys.mean())
        max_height = float(residual[component].max())
        mean_height = float(residual[component].mean())
        bbox_height = r1 - r0
        bbox_width = c1 - c0
        bbox_area_pixels = bbox_height * bbox_width
        density = float(area_pixels / max(1, bbox_area_pixels))
        orientation = "x" if bbox_width >= bbox_height else "y"
        particles.append(
            ParticleCluster(
                id=next_id,
                centroid_xy=(centroid_x, centroid_y),
                max_height=max_height,
                mean_height=mean_height,
                density=density,
                area_mm2=area_mm2,
                orientation=orientation,
                bbox=(r0, r1, c0, c1),
                mask=submask.copy(),
            )
        )
        next_id += 1

    return particles


def _fixtures_from_boxes(
    cloud: DownsampledCloud,
    residual: np.ndarray,
    board_mask: np.ndarray,
    mask: np.ndarray,
    boxes: Sequence[BoundingBox],
    config: TaskConfig,
) -> Tuple[List[Fixture], np.ndarray]:
    """根据标注矩形直接生成夹具集合及掩膜。"""
    fixtures: List[Fixture] = []
    fixture_mask = np.zeros_like(mask, dtype=bool)
    pixel_area = cloud.spacing_x * cloud.spacing_y
    step = max(1, cloud.step)
    height, width = mask.shape

    for idx, box in enumerate(boxes, start=1):
        x0 = max(0, int(np.floor(box.xmin / step)))
        x1 = min(width, int(np.ceil(box.xmax / step)))
        y0 = max(0, int(np.floor(box.ymin / step)))
        y1 = min(height, int(np.ceil(box.ymax / step)))
        if x1 <= x0 or y1 <= y0:
            continue
        region = np.zeros_like(mask, dtype=bool)
        region[y0:y1, x0:x1] = True
        region &= mask
        region &= board_mask
        if not region.any():
            continue
        fixture_mask |= region
        area_pixels = int(region.sum())
        area_mm2 = area_pixels * pixel_area
        xs = cloud.xs[region]
        ys = cloud.ys[region]
        centroid_x = float(xs.mean()) if xs.size else 0.0
        centroid_y = float(ys.mean()) if ys.size else 0.0
        max_height = float(residual[region].max()) if region.any() else 0.0
        radius = float(max(np.sqrt(area_mm2 / np.pi), config.tool_diameter * 0.5))
        fixtures.append(
            Fixture(
                id=idx,
                centroid_xy=(centroid_x, centroid_y),
                max_height=max_height,
                area_mm2=area_mm2,
                radius_mm=radius + config.tool_safety_margin,
                bbox=(y0, y1, x0, x1),
                mask=region[y0:y1, x0:x1].copy(),
            )
        )
    return fixtures, fixture_mask
