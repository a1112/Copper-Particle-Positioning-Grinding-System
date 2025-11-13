from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .config import TaskConfig
from .models import DownsampledCloud, PlaneModel


def _plane_from_points(points: np.ndarray) -> tuple[np.ndarray, float] | None:
    """由三个点估算平面，返回单位法向量与偏移。"""
    p0, p1, p2 = points
    v1 = p1 - p0
    v2 = p2 - p0
    normal = np.cross(v1, v2)
    norm = np.linalg.norm(normal)
    if norm < 1e-6:
        return None
    normal /= norm
    offset = -float(np.dot(normal, p0))
    return normal, offset


def _refine_plane(points: np.ndarray) -> tuple[np.ndarray, float]:
    """使用所有内点通过 SVD 精修平面参数。"""
    centroid = points.mean(axis=0)
    centered = points - centroid
    _, _, vh = np.linalg.svd(centered)
    normal = vh[-1]
    normal /= np.linalg.norm(normal)
    offset = -float(np.dot(normal, centroid))
    return normal, offset


def fit_board_plane(cloud: DownsampledCloud, config: TaskConfig) -> PlaneModel:
    """基于 RANSAC + SVD 拟合板面平面模型。"""
    valid_points = cloud.positions()
    if valid_points.shape[0] < 3:
        raise RuntimeError("Insufficient valid points to fit the board plane.")

    zs = cloud.zs[cloud.valid_mask]
    z_cutoff = float(np.percentile(zs, 35))
    candidate_mask = zs <= z_cutoff + 1.0
    candidate_points = valid_points[candidate_mask]
    if candidate_points.shape[0] < 3:
        candidate_points = valid_points

    rng = np.random.default_rng(42)
    max_iterations = 800
    distance_threshold = max(0.4, config.board_residual_threshold * 1.5)
    best_inliers = 0
    best_model: tuple[np.ndarray, float] | None = None

    for _ in range(max_iterations):
        if candidate_points.shape[0] < 3:
            break
        indices = rng.choice(candidate_points.shape[0], size=3, replace=False)
        maybe_plane = _plane_from_points(candidate_points[indices])
        if maybe_plane is None:
            continue
        normal, offset = maybe_plane
        distances = np.abs(candidate_points @ normal + offset)
        inlier_mask = distances < distance_threshold
        inlier_count = int(inlier_mask.sum())
        if inlier_count < max(100, int(0.02 * candidate_points.shape[0])):
            continue
        if inlier_count > best_inliers:
            refined_normal, refined_offset = _refine_plane(candidate_points[inlier_mask])
            best_model = (refined_normal, refined_offset)
            best_inliers = inlier_count

    if best_model is None:
        refined_normal, refined_offset = _refine_plane(candidate_points)
    else:
        refined_normal, refined_offset = best_model

    distances_full = np.abs(valid_points @ refined_normal + refined_offset)
    inliers_full = distances_full < max(0.5, config.board_residual_threshold * 2.0)
    rms = float(math.sqrt(np.mean(distances_full[inliers_full] ** 2)))
    inlier_ratio = float(inliers_full.sum() / distances_full.size)

    if refined_normal[2] < 0:
        refined_normal = -refined_normal
        refined_offset = -refined_offset

    return PlaneModel(
        normal=refined_normal,
        offset=float(refined_offset),
        rms_error=rms,
        inlier_ratio=inlier_ratio,
    )
