from __future__ import annotations

import numpy as np

from work.alg.task1.config import TaskConfig
from work.alg.task1.models import DownsampledCloud, PlaneModel
from work.alg.task1.path_planner import plan_toolpaths
from work.alg.task1.plane_fit import fit_board_plane
from work.alg.task1.segmentation import compute_board_mask, detect_particles


def _synthetic_cloud(size: int = 32) -> DownsampledCloud:
    xs, ys = np.meshgrid(np.linspace(0.0, 20.0, size), np.linspace(0.0, 10.0, size))
    zs = 2.0 + 0.08 * xs + 0.02 * ys
    noise = np.random.default_rng(123).normal(scale=0.01, size=xs.shape)
    zs = zs + noise
    valid_mask = np.ones_like(xs, dtype=bool)
    return DownsampledCloud(
        xs=xs.astype(np.float32),
        ys=ys.astype(np.float32),
        zs=zs.astype(np.float32),
        valid_mask=valid_mask,
        step=1,
        spacing_x=float(np.median(np.diff(xs, axis=1))),
        spacing_y=float(np.median(np.diff(ys, axis=0))),
    )


def test_fit_board_plane_recovers_model() -> None:
    config = TaskConfig()
    config.tool_diameter = 5.0
    config.finish_allowance = 0.1
    cloud = _synthetic_cloud()
    plane = fit_board_plane(cloud, config)
    predicted = plane.z_at(cloud.xs, cloud.ys)
    error = np.abs(predicted - cloud.zs)
    assert float(np.mean(error)) < 0.1
    assert plane.normal[2] > 0.9


def test_plan_toolpaths_generates_segments() -> None:
    config = TaskConfig()
    config.tool_diameter = 5.0
    config.finish_allowance = 0.1
    config.particle_keep_height = 0.2
    cloud = _synthetic_cloud(size=20)
    raw_normal = np.array([-0.08, -0.02, 1.0], dtype=np.float32)
    norm = float(np.linalg.norm(raw_normal))
    normal = (raw_normal / norm).astype(np.float32)
    offset = -2.0 / norm
    plane = PlaneModel(
        normal=normal.astype(np.float32),
        offset=offset,
        rms_error=0.0,
        inlier_ratio=1.0,
    )
    board_mask = compute_board_mask(cloud, plane, config)
    base_map = plane.z_at(cloud.xs, cloud.ys)
    residual = base_map - cloud.zs
    residual[5:10, 5:10] += 4.0
    particles = detect_particles(cloud, residual, board_mask, np.zeros_like(board_mask), config)
    assert particles, "Expected synthetic particle cluster to be detected."

    plan = plan_toolpaths(
        cloud=cloud,
        base_map=base_map,
        board_height=float(np.median(base_map)),
        particles=particles,
        fixture_mask=np.zeros_like(board_mask),
        config=config,
    )
    cut_segments = [seg for seg in plan.segments if seg.kind == "cut"]
    assert cut_segments, "Toolpath should include cutting segments."
    offsets = []
    xs = cloud.xs
    ys = cloud.ys
    for seg in cut_segments:
        distances = (xs - seg.start[0]) ** 2 + (ys - seg.start[1]) ** 2
        idx = np.unravel_index(np.argmin(distances), xs.shape)
        base_z = float(base_map[idx])
        offsets.append(base_z - seg.start[2])
    assert max(offsets) > config.finish_allowance
