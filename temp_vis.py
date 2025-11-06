from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

import cv2
import numpy as np

from .config import TaskConfig
from .models import Fixture, PipelineResult, ToolPathSegment


@dataclass(slots=True)
class _CanvasMapper:
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    size: int

    def to_pixel(self, x: float, y: float) -> Tuple[int, int]:
        width = self.size
        height = self.size
        span_x = max(self.max_x - self.min_x, 1e-3)
        span_y = max(self.max_y - self.min_y, 1e-3)
        u = (x - self.min_x) / span_x
        v = (y - self.min_y) / span_y
        px = int(np.clip(u * (width - 1), 0, width - 1))
        py = int(np.clip((1.0 - v) * (height - 1), 0, height - 1))
        return px, py

    def radius_to_pixels(self, radius_mm: float) -> int:
        span = max(self.max_x - self.min_x, self.max_y - self.min_y, 1e-3)
        scale = (self.size - 1) / span
        return max(1, int(radius_mm * scale))


def _project_points(mapper: _CanvasMapper, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
    coords = [mapper.to_pixel(float(x), float(y)) for x, y in zip(xs, ys)]
    return np.array(coords, dtype=np.int32)


def _draw_board(mapper: _CanvasMapper, result: PipelineResult) -> np.ndarray:
    canvas = np.full((mapper.size, mapper.size, 3), 30, dtype=np.uint8)
    xs = result.cloud.xs[result.board_mask]
    ys = result.cloud.ys[result.board_mask]
    if xs.size >= 3:
        points = _project_points(mapper, xs, ys)
        hull = cv2.convexHull(points)
        cv2.fillConvexPoly(canvas, hull, (70, 70, 70))
    return canvas


def _draw_particles(mapper: _CanvasMapper, canvas: np.ndarray, result: PipelineResult) -> None:
    for particle in result.particles:
        r0, r1, c0, c1 = particle.bbox
        mask = particle.mask
        rows, cols = np.nonzero(mask)
        world_x = result.cloud.xs[r0 + rows, c0 + cols]
        world_y = result.cloud.ys[r0 + rows, c0 + cols]
        points = _project_points(mapper, world_x, world_y)
        if points.shape[0] < 3:
            continue
        hull = cv2.convexHull(points)
        cv2.fillConvexPoly(canvas, hull, (60, 120, 255))
        centroid_px = mapper.to_pixel(*particle.centroid_xy)
        cv2.circle(canvas, centroid_px, 3, (255, 200, 0), -1)


def _draw_fixtures(mapper: _CanvasMapper, canvas: np.ndarray, fixtures: Sequence[Fixture]) -> None:
    for fixture in fixtures:
        center_px = mapper.to_pixel(*fixture.centroid_xy)
        radius_px = mapper.radius_to_pixels(fixture.radius_mm)
        cv2.circle(canvas, center_px, radius_px, (20, 20, 200), 2)
        cv2.circle(canvas, center_px, max(3, radius_px // 6), (0, 0, 255), -1)


def _draw_toolpaths(
    mapper: _CanvasMapper,
    base: np.ndarray,
    segments: Sequence[ToolPathSegment],
    max_segments: int,
) -> Tuple[np.ndarray, List[np.ndarray]]:
    overlay = base.copy()
    frames: List[np.ndarray] = []
    color_map = {
        "rapid": (70, 200, 255),
        "plunge": (200, 200, 200),
        "cut": (40, 220, 40),
        "retract": (255, 200, 70),
    }
    segment_counter = 0
    for segment in segments:
        start_px = mapper.to_pixel(segment.start[0], segment.start[1])
        end_px = mapper.to_pixel(segment.end[0], segment.end[1])
        color = color_map.get(segment.kind, (255, 255, 255))
        thickness = 2 if segment.kind == "cut" else 1
        cv2.line(overlay, start_px, end_px, color, thickness, lineType=cv2.LINE_AA)
        segment_counter += 1
        if segment.kind == "cut" and segment_counter <= max_segments:
            frames.append(overlay.copy())
    return overlay, frames


def _render_height_map(result: PipelineResult, mapper: _CanvasMapper) -> np.ndarray:
    residual = result.residual_map.copy()
    valid = result.board_mask & result.cloud.valid_mask
    if not np.any(valid):
        return np.zeros((mapper.size, mapper.size, 3), dtype=np.uint8)
    values = residual[valid]
    vmin = float(np.percentile(values, 5))
    vmax = float(np.percentile(values, 99))
    rng = max(vmax - vmin, 1e-3)
    normalized = np.clip((residual - vmin) / rng, 0.0, 1.0)
    canvas = np.zeros((mapper.size, mapper.size), dtype=np.float32)
    xs = result.cloud.xs
    ys = result.cloud.ys
    for r in range(xs.shape[0]):
        for c in range(xs.shape[1]):
            if not valid[r, c]:
                continue
            px, py = mapper.to_pixel(float(xs[r, c]), float(ys[r, c]))
            canvas[py, px] = max(canvas[py, px], normalized[r, c])
    colored = cv2.applyColorMap((canvas * 255).astype(np.uint8), cv2.COLORMAP_JET)
    return colored


def _board_fixture_map(result: PipelineResult) -> np.ndarray:
    board_mask = result.board_main_region_full
    canvas = np.zeros((*board_mask.shape, 3), dtype=np.uint8)
    canvas[board_mask] = (255, 0, 0)
    for box in result.fixture_boxes:
        cv2.rectangle(canvas, (box.xmin, box.ymin), (box.xmax, box.ymax), (0, 0, 255), 2)
    return canvas


def _board_fixture_hsv(result: PipelineResult) -> np.ndarray:
    board_mask = result.board_main_region_full
    bgr = np.zeros((*board_mask.shape, 3), dtype=np.uint8)
    bgr[board_mask] = (180, 180, 240)
    for box in result.fixture_boxes:
        cv2.rectangle(bgr, (box.xmin, box.ymin), (box.xmax, box.ymax), (0, 0, 255), 2)
    bgr[~board_mask] = 0
    return bgr


def _particle_hsv_map(result: PipelineResult, config: TaskConfig) -> np.ndarray:
    board_mask = result.board_main_region_full
    fixture_mask = result.fixture_mask_full
    z_image = result.z_image_full
    base_map = result.base_height_map
    height = base_map - z_image
    valid_depth = result.z_image_full > 0
    allowed = board_mask & valid_depth & ~fixture_mask
    particles = allowed & (height >= config.particle_keep_height)

    hsv = np.zeros((*board_mask.shape, 3), dtype=np.uint8)
    hsv[..., 2] = 0

    hsv[allowed, 0] = 90
    hsv[allowed, 1] = 60
    hsv[allowed, 2] = 120

    if particles.any():
        normalized = np.clip(height / max(config.height_display_max, 1e-3), 0.0, 1.0)
        hue = (30 * (1.0 - normalized)).astype(np.uint8)
        hsv[particles, 0] = hue[particles]
        hsv[particles, 1] = 255
        hsv[particles, 2] = 255

    hsv[fixture_mask, 0] = 0
    hsv[fixture_mask, 1] = 255
    hsv[fixture_mask, 2] = 200

    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    bgr[~board_mask & ~fixture_mask] = 0
    return bgr


def _reference_hsv_map(result: PipelineResult, config: TaskConfig) -> np.ndarray:
    ref = config.reference_plane_z
    height = np.zeros_like(result.z_image_full, dtype=np.float32)
    valid = result.z_image_full > 0
    height[valid] = np.minimum(np.abs(result.z_image_full[valid] - ref), config.height_display_max)
    normalized = np.clip(height / max(config.height_display_max, 1e-3), 0.0, 1.0)
    hsv = np.zeros((*height.shape, 3), dtype=np.uint8)
    hsv[..., 0] = ((1.0 - normalized) * 60).astype(np.uint8)  # 0-60 hue from red->yellow
    hsv[..., 1] = np.where(valid, 255, 0).astype(np.uint8)
    hsv[..., 2] = (normalized * 255).astype(np.uint8)
    hsv[~valid] = 0
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def _particle_mask_map(result: PipelineResult, config: TaskConfig) -> np.ndarray:
    height = result.base_height_map - result.z_image_full
    valid = result.z_image_full > 0
    mask = valid & result.board_main_region_full & (height >= config.particle_keep_height)
    return (mask.astype(np.uint8) * 255)


def _height_jet_map(result: PipelineResult, config: TaskConfig) -> np.ndarray:
    height = result.base_height_map - result.z_image_full
    valid = (result.z_image_full > 0) & result.board_mask_full
    clipped = np.zeros_like(height, dtype=np.float32)
    clipped[valid] = np.clip(height[valid], 0.0, config.height_display_max)
    normalized = (clipped / max(config.height_display_max, 1e-3)).astype(np.float32)
    jet = cv2.applyColorMap((normalized * 255).astype(np.uint8), cv2.COLORMAP_JET)
    jet[~valid] = 0
    return jet


def _height_contour_map(result: PipelineResult, config: TaskConfig) -> np.ndarray:
    height = result.base_height_map - result.z_image_full
    valid = (result.z_image_full > 0) & result.board_mask_full
    clipped = np.zeros_like(height, dtype=np.float32)
    clipped[valid] = np.clip(height[valid], 0.0, config.height_display_max)
    scaled = (clipped / max(config.height_display_max, 1e-3) * 255).astype(np.uint8)
    contour_img = np.zeros((*height.shape, 3), dtype=np.uint8)
    step_mm = max(5.0, config.height_display_max / 20.0)
    levels = np.arange(step_mm, config.height_display_max + step_mm, step_mm)
    for level in levels:
        level_val = int(np.clip(level / max(config.height_display_max, 1e-3) * 255, 0, 255))
        thresh = cv2.inRange(scaled, level_val, 255)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(contour_img, contours, -1, (255, 255, 255), 1)
    contour_img[~valid] = 0
    return contour_img


def generate_visualizations(result: PipelineResult, config: TaskConfig) -> Dict[str, object]:
    xs = result.cloud.xs[result.board_mask]
    ys = result.cloud.ys[result.board_mask]
    if xs.size == 0 or ys.size == 0:
        raise RuntimeError("Unable to build visualization without board points.")
    mapper = _CanvasMapper(
        min_x=float(xs.min()),
        max_x=float(xs.max()),
        min_y=float(ys.min()),
        max_y=float(ys.max()),
        size=config.visualization_size,
    )

    overview = _draw_board(mapper, result)
    _draw_particles(mapper, overview, result)
    _draw_fixtures(mapper, overview, result.fixtures)

    path_overlay, frames = _draw_toolpaths(mapper, overview.copy(), result.toolpaths.segments, config.simulate_limit_segments)

    payload: Dict[str, object] = {
        "overview": overview,
        "toolpath": path_overlay,
        "frames": frames if config.step_simulation else [],
    }

    if config.save_height_map:
        payload["height_map"] = _render_height_map(result, mapper)

    payload["board_fixture_map"] = _board_fixture_map(result)
    payload["board_fixture_hsv"] = _board_fixture_hsv(result)
    payload["particle_hsv"] = _particle_hsv_map(result, config)
    payload["base_height_map"] = result.base_height_map
    payload["reference_hsv"] = _reference_hsv_map(result, config)
    payload["fixture_mask"] = (result.fixture_mask_full.astype(np.uint8) * 255)
    payload["board_mask"] = result.board_residual_full.astype(np.float32)
    payload["board_main_region"] = (result.board_main_region_full.astype(np.uint8) * 255)
    payload["particle_mask"] = _particle_mask_map(result, config)
    payload["height_jet"] = _height_jet_map(result, config)
    payload["height_contours"] = _height_contour_map(result, config)

    return payload

