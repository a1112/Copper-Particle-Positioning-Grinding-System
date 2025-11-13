from __future__ import annotations

import math
from typing import List, Sequence, Tuple

import cv2
import numpy as np

from .config import TaskConfig
from .models import (
    DownsampledCloud,
    ParticleCluster,
    ToolPathPlan,
    ToolPathSegment,
)


def _contiguous_segments(mask: np.ndarray) -> List[Tuple[int, int]]:
    """在一维布尔数组内查找连续的 True 区间。"""
    if mask.ndim != 1:
        raise ValueError("Expected 1D mask for contiguous segment extraction.")
    if mask.dtype != np.bool_:
        mask = mask.astype(bool)
    if not mask.any():
        return []
    padded = np.pad(mask.astype(np.int8), (1, 1), constant_values=0)
    diff = np.diff(padded)
    starts = np.where(diff == 1)[0]
    ends = np.where(diff == -1)[0]
    return [(int(s), int(e)) for s, e in zip(starts, ends)]


def _dilate_mask(mask: np.ndarray, radius_mm: float, spacing_x: float, spacing_y: float) -> np.ndarray:
    """根据物理半径在网格上膨胀掩膜。"""
    radius_x = max(1, int(math.ceil(radius_mm / max(spacing_x, 1e-3))))
    radius_y = max(1, int(math.ceil(radius_mm / max(spacing_y, 1e-3))))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * radius_y + 1, 2 * radius_x + 1))
    dilated = cv2.dilate(mask.astype(np.uint8), kernel)
    return dilated.astype(bool)


def plan_toolpaths(
    cloud: DownsampledCloud,
    base_map: np.ndarray,
    board_height: float,
    particles: Sequence[ParticleCluster],
    fixture_mask: np.ndarray,
    config: TaskConfig,
) -> ToolPathPlan:
    """按颗粒密度生成刀路计划，自动避开夹具与安全高度。"""
    plan = ToolPathPlan()
    segment_counter = 1
    safe_height = board_height + config.clearance_height

    inflated_fixture = _dilate_mask(
        fixture_mask,
        radius_mm=config.tool_diameter * 0.5 + config.tool_safety_margin,
        spacing_x=cloud.spacing_x,
        spacing_y=cloud.spacing_y,
    )

    for cluster in particles:
        max_removal = max(0.0, cluster.max_height - config.finish_allowance)
        if max_removal <= 1e-3:
            continue

        density = cluster.density
        feed_rate = config.feed_for_density(density)
        cut_step = max(0.1, config.cut_depth_for_density(density))
        num_passes = max(1, int(math.ceil(max_removal / cut_step)))

        r0, r1, c0, c1 = cluster.bbox
        cluster_mask = np.zeros_like(cloud.valid_mask, dtype=bool)
        cluster_mask[r0:r1, c0:c1] = cluster.mask
        tool_radius = config.tool_diameter * 0.5 + config.tool_safety_margin
        dilated_cluster = _dilate_mask(cluster_mask, tool_radius, cloud.spacing_x, cloud.spacing_y)
        dilated_cluster &= ~inflated_fixture
        if not dilated_cluster.any():
            continue
        current_safe: Tuple[float, float, float] | None = None

        for pass_index in range(num_passes):
            removal = min((pass_index + 1) * cut_step, max_removal)
            residual_after_pass = max(cluster.max_height - removal, config.finish_allowance)
            direction = 1

            if cluster.orientation == "x":
                sweep_indices = range(r0, r1)
            else:
                sweep_indices = range(c0, c1)

            for idx in sweep_indices:
                if cluster.orientation == "x":
                    row_mask = dilated_cluster[idx, c0:c1]
                    segments = _contiguous_segments(row_mask)
                else:
                    col_mask = dilated_cluster[r0:r1, idx]
                    segments = _contiguous_segments(col_mask)
                if not segments:
                    direction *= -1
                    continue
                if direction < 0:
                    segments = segments[::-1]

                for seg_start, seg_end in segments:
                    if cluster.orientation == "x":
                        start_col = c0 + (seg_end - 1 if direction < 0 else seg_start)
                        end_col = c0 + (seg_start if direction < 0 else seg_end - 1)
                        row_index = idx
                        x_start = float(cloud.xs[row_index, start_col])
                        y_start = float(cloud.ys[row_index, start_col])
                        x_end = float(cloud.xs[row_index, end_col])
                        y_end = float(cloud.ys[row_index, end_col])
                    else:
                        start_row = r0 + (seg_end - 1 if direction < 0 else seg_start)
                        end_row = r0 + (seg_start if direction < 0 else seg_end - 1)
                        col_index = idx
                        x_start = float(cloud.xs[start_row, col_index])
                        y_start = float(cloud.ys[start_row, col_index])
                        x_end = float(cloud.xs[end_row, col_index])
                        y_end = float(cloud.ys[end_row, col_index])

                    length_mm = math.hypot(x_end - x_start, y_end - y_start)
                    if length_mm < config.min_segment_length_mm:
                        continue

                    if cluster.orientation == "x":
                        base_start = float(base_map[row_index, start_col])
                        base_end = float(base_map[row_index, end_col])
                    else:
                        base_start = float(base_map[start_row, col_index])
                        base_end = float(base_map[end_row, col_index])
                    cut_start_z = base_start - residual_after_pass
                    cut_end_z = base_end - residual_after_pass
                    target_safe_start = (x_start, y_start, safe_height)

                    if current_safe is None:
                        current_safe = target_safe_start
                    if any(abs(a - b) > 1e-3 for a, b in zip(current_safe, target_safe_start)):
                        plan.add_segment(
                            ToolPathSegment(
                                segment_id=segment_counter,
                                cluster_id=cluster.id,
                                pass_index=pass_index,
                                kind="rapid",
                                start=current_safe,
                                end=target_safe_start,
                                feed_rate=config.travel_speed_mm_min,
                            )
                        )
                        segment_counter += 1
                        current_safe = target_safe_start

                    plan.add_segment(
                        ToolPathSegment(
                            segment_id=segment_counter,
                            cluster_id=cluster.id,
                            pass_index=pass_index,
                            kind="plunge",
                            start=current_safe,
                            end=(x_start, y_start, cut_start_z),
                            feed_rate=feed_rate * 0.5,
                        )
                    )
                    segment_counter += 1

                    plan.add_segment(
                        ToolPathSegment(
                            segment_id=segment_counter,
                            cluster_id=cluster.id,
                            pass_index=pass_index,
                            kind="cut",
                            start=(x_start, y_start, cut_start_z),
                            end=(x_end, y_end, cut_end_z),
                            feed_rate=feed_rate,
                        )
                    )
                    segment_counter += 1

                    retract_end = (x_end, y_end, safe_height)
                    plan.add_segment(
                        ToolPathSegment(
                            segment_id=segment_counter,
                            cluster_id=cluster.id,
                            pass_index=pass_index,
                            kind="retract",
                            start=(x_end, y_end, cut_end_z),
                            end=retract_end,
                            feed_rate=config.travel_speed_mm_min,
                        )
                    )
                    segment_counter += 1
                    current_safe = retract_end

                direction *= -1

    return plan
