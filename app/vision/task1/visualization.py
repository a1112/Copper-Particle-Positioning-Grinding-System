from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple
from pathlib import Path

import cv2
import numpy as np

from .config import TaskConfig
from .models import Fixture, PipelineResult, ToolPathSegment


@dataclass(slots=True)
class _CanvasMapper:
    """负责将毫米坐标映射到可视化画布像素坐标。"""

    min_x: float
    max_x: float
    min_y: float
    max_y: float
    size: int

    def to_pixel(self, x: float, y: float) -> Tuple[int, int]:
        """将物理坐标 (x, y) 转换为画布像素位置。"""
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
        """将半径（毫米）换算成画布像素长度。"""
        span = max(self.max_x - self.min_x, self.max_y - self.min_y, 1e-3)
        scale = (self.size - 1) / span
        return max(1, int(radius_mm * scale))


def _project_points(mapper: _CanvasMapper, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
    """批量映射 (x, y) 坐标到像素位置并返回整型数组。"""
    coords = [mapper.to_pixel(float(x), float(y)) for x, y in zip(xs, ys)]
    return np.array(coords, dtype=np.int32)


def _draw_board(mapper: _CanvasMapper, result: PipelineResult) -> np.ndarray:
    """绘制板面凸包作为背景。"""
    canvas = np.full((mapper.size, mapper.size, 3), 30, dtype=np.uint8)
    xs = result.cloud.xs[result.board_mask]
    ys = result.cloud.ys[result.board_mask]
    if xs.size >= 3:
        points = _project_points(mapper, xs, ys)
        hull = cv2.convexHull(points)
        cv2.fillConvexPoly(canvas, hull, (70, 70, 70))
    return canvas


def _draw_particles(mapper: _CanvasMapper, canvas: np.ndarray, result: PipelineResult) -> None:
    """以凸包填充的方式渲染颗粒簇。"""
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
    """在画布上绘制夹具位置及安全半径。"""
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
    """在画布上叠加刀路段，并可选输出逐段帧序列。"""
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
    """将残差高度映射为三通道伪彩色图。"""
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
    """绘制主板拟合区域及夹具矩形轮廓。"""
    board_mask = result.board_main_region_full
    canvas = np.zeros((*board_mask.shape, 3), dtype=np.uint8)
    canvas[board_mask] = (255, 0, 0)
    for box in result.fixture_boxes:
        cv2.rectangle(canvas, (box.xmin, box.ymin), (box.xmax, box.ymax), (0, 0, 255), 2)
    return canvas


def _board_fixture_hsv(result: PipelineResult) -> np.ndarray:
    """以伪彩方式突出主板区域，并用红框标记夹具。"""
    board_mask = result.board_main_region_full
    bgr = np.zeros((*board_mask.shape, 3), dtype=np.uint8)
    bgr[board_mask] = (180, 180, 240)
    for box in result.fixture_boxes:
        cv2.rectangle(bgr, (box.xmin, box.ymin), (box.xmax, box.ymax), (0, 0, 255), 2)
    bgr[~board_mask] = 0
    return bgr


def _particle_hsv_map(result: PipelineResult, config: TaskConfig) -> np.ndarray:
    """渲染颗粒密度和高度，同时区分夹具区域。"""
    board_mask = result.board_mask_full
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
    height[valid] = np.abs(result.z_image_full[valid] - ref)
    positives = height[(height > 0) & valid]
    if positives.size:
        min_val = float(positives.min())
        max_val = float(positives.max())
    else:
        min_val = 0.0
        max_val = 1.0
    denom = max(max_val - min_val, 1e-6)
    normalized = np.zeros_like(height, dtype=np.float32)
    mask = (height > 0) & valid
    normalized[mask] = np.clip((height[mask] - min_val) / denom, 0.0, 1.0)
    hsv = np.zeros((*height.shape, 3), dtype=np.uint8)
    hsv[..., 0] = ((1.0 - normalized) * 60).astype(np.uint8)  # 0-60 hue from red->yellow
    hsv[..., 1] = np.where(valid, 255, 0).astype(np.uint8)
    hsv[..., 2] = (normalized * 255).astype(np.uint8)
    hsv[~valid] = 0
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def _particle_mask_map(result: PipelineResult, config: TaskConfig) -> np.ndarray:
    """生成颗粒二值掩膜，并上采样到原始分辨率后返回。"""
    # 在降采样网格上合成颗粒掩码
    h_down, w_down = result.cloud.valid_mask.shape
    mask_down = np.zeros((h_down, w_down), dtype=np.uint8)
    for particle in result.particles:
        r0, r1, c0, c1 = particle.bbox
        if r1 <= r0 or c1 <= c0:
            continue
        sub = particle.mask.astype(np.uint8)
        mask_down[r0:r1, c0:c1] = np.maximum(mask_down[r0:r1, c0:c1], sub)

    # 上采样至全分辨率
    full_h, full_w = result.z_image_full.shape
    mask_full = cv2.resize(mask_down, (full_w, full_h), interpolation=cv2.INTER_NEAREST).astype(bool)

    # 仅保留有效深度与板面范围，且排除夹具区域
    valid = result.z_image_full > 0
    mask_full &= valid & result.board_mask_full & ~result.fixture_mask_full
    return (mask_full.astype(np.uint8) * 255)


def _height_jet_map(result: PipelineResult, config: TaskConfig) -> np.ndarray:
    """将高度差值映射为 Jet 伪彩色热力图。"""
    ref = config.reference_plane_z
    height = np.clip(ref - result.z_image_full, 0.0, None)
    valid = (result.z_image_full > 0) & result.board_main_region_full
    positives = height[(height > 0) & valid]
    if positives.size:
        min_val = float(positives.min())
        max_val = float(positives.max())
    else:
        min_val = 0.0
        max_val = 1.0
    denom = max(max_val - min_val, 1e-6)
    normalized = np.zeros_like(height, dtype=np.float32)
    mask = (height > 0) & valid
    normalized[mask] = np.clip((height[mask] - min_val) / denom, 0.0, 1.0)
    jet = cv2.applyColorMap((normalized * 255).astype(np.uint8), cv2.COLORMAP_JET)
    jet[~valid] = 0
    return jet


def _height_contour_map(result: PipelineResult, config: TaskConfig) -> np.ndarray:
    """提取高度分层等值线，用于观察板面波动。"""
    ref = config.reference_plane_z
    height = np.clip(ref - result.z_image_full, 0.0, None)
    valid = (result.z_image_full > 0) & result.board_main_region_full
    fixture_mask = result.fixture_mask_full
    if config.fixture_near_distance_px > 0:
        radius = int(config.fixture_near_distance_px)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * radius + 1, 2 * radius + 1))
        expanded = cv2.dilate(fixture_mask.astype(np.uint8), kernel, iterations=1).astype(bool)
    else:
        expanded = fixture_mask
    valid &= ~expanded
    positives = height[(height > 0) & valid]
    if positives.size:
        min_val = float(positives.min())
        max_val = float(positives.max())
    else:
        min_val = 0.0
        max_val = 1.0
    mask = (height > 0) & valid
    contour_img = np.zeros((*height.shape, 3), dtype=np.uint8)
    if positives.size:
        step_mm = 2.0
    else:
        step_mm = 2.0
    levels = np.arange(min_val + step_mm, max_val + step_mm, step_mm)
    colors = [
        (255, 0, 255),    # magenta
        (0, 255, 255),    # cyan
        (0, 128, 255),    # orange
        (0, 255, 0),      # green
        (0, 0, 255),      # red
        (255, 255, 0),    # yellow
        (255, 0, 0),      # blue (BGR)
    ]
    index = 0
    # 面积阈值：过滤“零星小点”噪声等小连通域
    min_area_px = max(32, int(0.0001 * height.size))  # ~0.01% 像素或至少 32 像素
    for level in levels:
        lower = np.clip(level - 1e-3, min_val, None)
        upper = level + 1e-3
        band = np.zeros_like(height, dtype=np.uint8)
        band[(height >= lower) & (height < upper) & mask] = 255
        if band.any():
            contours, _ = cv2.findContours(band, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # 过滤掉面积过小的轮廓（零星小点）
            contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= float(min_area_px)]
            if not contours:
                continue
            color = colors[index % len(colors)]
            cv2.drawContours(contour_img, contours, -1, color, 2)
            index += 1
    contour_img[~valid] = 0
    return contour_img


def _center_path_map(result: PipelineResult, mapper: _CanvasMapper) -> np.ndarray:
    """绘制仅包含切削段的主轴中心路径。"""
    canvas = np.zeros((mapper.size, mapper.size, 3), dtype=np.uint8)
    for segment in result.toolpaths.segments:
        if segment.kind != "cut":
            continue
        start_px = mapper.to_pixel(segment.start[0], segment.start[1])
        end_px = mapper.to_pixel(segment.end[0], segment.end[1])
        cv2.line(canvas, start_px, end_px, (0, 255, 255), 1, cv2.LINE_AA)
    return canvas

def _fixture_removed_z_map(result: PipelineResult) -> np.ndarray:
    """返回夹具区域置零后的 Z 高度图。"""
    z_clean = result.z_image_full.copy()
    z_clean[result.fixture_mask_full] = 0.0
    return z_clean.astype(np.float32)


def generate_visualizations(result: PipelineResult, config: TaskConfig) -> Dict[str, object]:
    """汇总生成调试用的图像矩阵与路径演示帧。"""
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

    payload: Dict[str, object] = {
        "overview": overview,
    }

    if config.save_height_map:
        payload["height_map"] = _render_height_map(result, mapper)

    payload["board_fixture_map"] = _board_fixture_map(result)
    payload["fixture_mask"] = (result.fixture_mask_full.astype(np.uint8) * 255)
    payload["board_mask"] = result.board_residual_full.astype(np.float32)
    payload["board_main_region"] = (result.board_main_region_full.astype(np.uint8) * 255)
    payload["particle_mask"] = _particle_mask_map(result, config)
    payload["height_jet"] = _height_jet_map(result, config)
    payload["height_contours"] = _height_contour_map(result, config)
    payload["spindle_path"] = _center_path_map(result, mapper)
    payload["z_without_fixtures"] = _fixture_removed_z_map(result)

    # 叠加输出：将 particle_mask 与 src_IMG_Color.png（若存在）半透明叠加
    def _load_fixture_color_image() -> np.ndarray | None:
        candidates: List[Path] = []
        if config.fixture_annotation:
            p = Path(config.fixture_annotation)
            if p.suffix.lower() != ".xml":
                candidates.append(p)
        # 默认从采集目录尝试
        candidates.append(config.source_dir / "src_IMG_Color.png")
        candidates.append(config.source_dir / "src_IMG_Color.tif")
        candidates.append(config.source_dir / "src_IMG_Color.jpg")
        candidates.append(config.source_dir / "src_IMG_Color.jpeg")
        for path in candidates:
            if path.exists():
                img = cv2.imread(str(path), cv2.IMREAD_COLOR)
                if img is not None:
                    h, w = result.z_image_full.shape
                    if img.shape[:2] != (h, w):
                        img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
                    return img
        return None

    pmask = payload["particle_mask"]  # uint8 0/255
    if isinstance(pmask, np.ndarray) and pmask.ndim == 2:
        h, w = pmask.shape
        pmask_color = np.zeros((h, w, 3), dtype=np.uint8)
        pmask_bool = pmask > 0
        pmask_color[pmask_bool] = (60, 220, 60)  # 绿色颗粒

        fixture_img = _load_fixture_color_image()
        if fixture_img is None:
            # 回退为夹具掩码可视化（红色）
            fixture_img = np.zeros((h, w, 3), dtype=np.uint8)
            fmask = result.fixture_mask_full
            if fmask.shape != (h, w):
                fmask = cv2.resize(fmask.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST).astype(bool)
            fixture_img[fmask] = (0, 0, 255)

        overlay = cv2.addWeighted(pmask_color, 0.7, fixture_img, 0.3, 0.0)
        payload["particle_mask_overlay"] = overlay

    return payload
