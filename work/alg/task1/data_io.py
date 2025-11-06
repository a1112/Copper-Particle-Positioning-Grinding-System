from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from .config import TaskConfig
from .models import DownsampledCloud

POINT_CLOUD_FILES = {
    "x": "src_IMG_PointCloud_X.tif",
    "y": "src_IMG_PointCloud_Y.tif",
    "z": "src_IMG_PointCloud_Z.tif",
}


def _load_tiff(path: Path) -> np.ndarray:
    """读取 TIFF 图像并转换为 float32 数组。"""
    array = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if array is None:
        raise FileNotFoundError(f"Unable to read capture file: {path}")
    return array.astype(np.float32)


def _estimate_spacing(xs: np.ndarray, ys: np.ndarray, axis: int) -> float:
    """估计点云在指定方向上的像素间距（毫米）。"""
    if axis == 1:
        dx = np.diff(xs, axis=1)
        dy = np.diff(ys, axis=1)
    else:
        dx = np.diff(xs, axis=0)
        dy = np.diff(ys, axis=0)
    distances = np.sqrt(dx**2 + dy**2)
    valid = distances[np.isfinite(distances) & (distances > 1e-4)]
    if valid.size == 0:
        return 1.0
    return float(np.median(valid))


def load_downsampled_cloud(config: TaskConfig) -> DownsampledCloud:
    """按配置下采样点云并补充有效掩膜、步长等元信息。"""
    source_dir = config.source_dir
    xs_full = _load_tiff(source_dir / POINT_CLOUD_FILES["x"])
    ys_full = _load_tiff(source_dir / POINT_CLOUD_FILES["y"])
    zs_full = _load_tiff(source_dir / POINT_CLOUD_FILES["z"])
    if xs_full.shape != ys_full.shape or xs_full.shape != zs_full.shape:
        raise ValueError("Point cloud TIFF shapes differ; cannot proceed.")

    step = max(1, config.grid_step)
    xs = xs_full[::step, ::step]
    ys = ys_full[::step, ::step]
    zs = zs_full[::step, ::step]
    stacked = np.stack([xs, ys, zs], axis=-1)
    norms = np.linalg.norm(stacked, axis=-1)
    valid_mask = norms > config.valid_epsilon

    spacing_x = _estimate_spacing(xs, ys, axis=1)
    spacing_y = _estimate_spacing(xs, ys, axis=0)
    return DownsampledCloud(
        xs=xs,
        ys=ys,
        zs=zs,
        valid_mask=valid_mask,
        step=step,
        spacing_x=spacing_x,
        spacing_y=spacing_y,
    )
