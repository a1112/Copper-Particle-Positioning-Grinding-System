from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence, Tuple

import numpy as np

from .annotations import BoundingBox


@dataclass(slots=True)
class PlaneModel:
    """板面拟合得到的平面参数。"""

    normal: np.ndarray
    offset: float
    rms_error: float
    inlier_ratio: float

    def z_at(self, x: np.ndarray | float, y: np.ndarray | float) -> np.ndarray | float:
        """根据平面方程计算给定 (x, y) 的 Z 高度。"""
        c = float(self.normal[2])
        if abs(c) < 1e-6:
            raise ValueError("Plane normal is parallel to Z axis; cannot solve for Z.")
        return (-self.offset - self.normal[0] * x - self.normal[1] * y) / c


@dataclass(slots=True)
class DownsampledCloud:
    """下采样后的点云及其有效掩膜。"""

    xs: np.ndarray
    ys: np.ndarray
    zs: np.ndarray
    valid_mask: np.ndarray
    step: int
    spacing_x: float
    spacing_y: float

    def positions(self) -> np.ndarray:
        """返回有效像素对应的 (x, y, z) 坐标集合。"""
        stacked = np.stack([self.xs, self.ys, self.zs], axis=-1)
        return stacked[self.valid_mask]

    @property
    def shape(self) -> Tuple[int, int]:
        """返回下采样网格的尺寸。"""
        return self.xs.shape

    def residual(self, plane: PlaneModel) -> np.ndarray:
        """计算点云相对于平面模型的残差高度。"""
        plane_z = plane.z_at(self.xs, self.ys)
        return self.zs - plane_z


@dataclass(slots=True)
class Fixture:
    """以毫米为单位的夹具几何描述。"""

    id: int
    centroid_xy: Tuple[float, float]
    max_height: float
    area_mm2: float
    radius_mm: float
    bbox: Tuple[int, int, int, int]
    mask: np.ndarray


@dataclass(slots=True)
class PixelFixture:
    """以像素分辨率表示的夹具信息。"""

    id: int
    bbox: Tuple[int, int, int, int]
    mask: np.ndarray
    centroid: Tuple[float, float]
    peak_z: float
    area_px: int


@dataclass(slots=True)
class ParticleCluster:
    """毫米尺度下的颗粒聚类特征。"""

    id: int
    centroid_xy: Tuple[float, float]
    max_height: float
    mean_height: float
    density: float
    area_mm2: float
    orientation: str
    bbox: Tuple[int, int, int, int]
    mask: np.ndarray


@dataclass(slots=True)
class PixelParticleCluster:
    """以像素为单位描述的颗粒聚类（调试用）。"""

    id: int
    bbox: Tuple[int, int, int, int]
    mask: np.ndarray
    centroid: Tuple[float, float]
    max_height: float
    mean_height: float
    area_px: int
    density: float
    orientation: str


@dataclass(slots=True)
class ToolPathSegment:
    """可执行的单段刀路指令。"""

    segment_id: int
    cluster_id: int
    pass_index: int
    kind: str
    start: Tuple[float, float, float]
    end: Tuple[float, float, float]
    feed_rate: float


@dataclass(slots=True)
class PixelPathSegment:
    """像素坐标系中的刀路段，用于可视化。"""

    segment_id: int
    cluster_id: int
    pass_index: int
    kind: str
    start_rc: Tuple[float, float]
    end_rc: Tuple[float, float]
    feed_rate: float
    target_z: float


@dataclass(slots=True)
class ToolPathPlan:
    """刀路集合容器。"""

    segments: List[ToolPathSegment] = field(default_factory=list)

    def add_segment(self, segment: ToolPathSegment) -> None:
        """追加刀路段。"""
        self.segments.append(segment)


@dataclass(slots=True)
class PipelineResult:
    """任务管线的汇总输出对象。"""

    cloud: DownsampledCloud
    plane: PlaneModel
    board_mask: np.ndarray
    residual_map: np.ndarray
    board_height: float
    board_mask_full: np.ndarray
    board_main_region_full: np.ndarray
    board_residual_full: np.ndarray
    fixture_mask_full: np.ndarray
    base_height_map: np.ndarray
    z_image_full: np.ndarray
    fixture_boxes: Sequence[BoundingBox]
    fixtures: Sequence[Fixture]
    particles: Sequence[ParticleCluster]
    toolpaths: ToolPathPlan
