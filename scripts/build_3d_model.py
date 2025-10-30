#!/usr/bin/env python3
"""
Utility to process structured-light point clouds stored in D:\SaveData\current.

The script reads the X/Y/Z point cloud TIFFs (default: rts_X1/Y1/Z1.tif), optionally downsamples, and exports both:
1. An OBJ surface mesh suitable for Qt Quick 3D usage.
2. A PLY point cloud (when open3d is available) that preserves the non-closed geometry for external tools.

When ``--show`` is supplied the generated point cloud is previewed with Open3D.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Tuple

import cv2
import numpy as np

try:  # optional visualization/export dependency
    import open3d as o3d  # type: ignore

    _O3D_AVAILABLE = True
except ImportError:  # pragma: no cover - best effort when library missing
    o3d = None  # type: ignore[assignment]
    _O3D_AVAILABLE = False


DEFAULT_SOURCE_DIR = Path(r"D:\SaveData\current")
DEFAULT_OUTPUT = Path("TestData") / "models" / "generated_surface.obj"
DEFAULT_EXPORT_COPY = DEFAULT_SOURCE_DIR / "generated_surface.obj"
DEFAULT_POINT_CLOUD = Path("TestData") / "models" / "generated_point_cloud.ply"
DEFAULT_POINT_CLOUD_COPY = DEFAULT_SOURCE_DIR / "generated_point_cloud.ply"
DEFAULT_FILE_X = "rts_X1.tif"
DEFAULT_FILE_Y = "rts_Y1.tif"
DEFAULT_FILE_Z = "rts_Z1.tif"


@dataclass(frozen=True)
class PointCloud:
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray

    @property
    def shape(self) -> Tuple[int, int]:
        return self.x.shape


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build triangulated/point-cloud representations from structured-light captures."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="Directory containing the structured-light TIFFs (default: %(default)s).",
    )
    parser.add_argument(
        "--file-x",
        type=str,
        default=DEFAULT_FILE_X,
        help="Filename containing X coordinates (default: %(default)s).",
    )
    parser.add_argument(
        "--file-y",
        type=str,
        default=DEFAULT_FILE_Y,
        help="Filename containing Y coordinates (default: %(default)s).",
    )
    parser.add_argument(
        "--file-z",
        type=str,
        default=DEFAULT_FILE_Z,
        help="Filename containing Z coordinates (default: %(default)s).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="OBJ file to write for Qt Quick 3D (relative paths resolved from repo root).",
    )
    parser.add_argument(
        "--copy-to",
        type=Path,
        default=DEFAULT_EXPORT_COPY,
        help="Optional additional OBJ copy for external tools (default: %(default)s).",
    )
    parser.add_argument(
        "--step",
        type=int,
        default=4,
        help="Sampling step to downsample the grid (>=1). Larger values create smaller meshes/point clouds.",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=600 * 600,
        help="Optional limit on number of sampled vertices; step is increased until satisfied.",
    )
    parser.add_argument(
        "--z-scale",
        type=float,
        default=1.0,
        help="Optional scale factor applied to the Z axis.",
    )
    parser.add_argument(
        "--flip-y",
        action="store_true",
        help="Flip the Y axis to match right-handed coordinates used in Qt Quick 3D and Open3D.",
    )
    parser.add_argument(
        "--valid-epsilon",
        type=float,
        default=1e-6,
        help="Minimum distance from origin to treat a sample as valid (default: %(default)s).",
    )
    parser.add_argument(
        "--point-cloud",
        type=Path,
        default=DEFAULT_POINT_CLOUD,
        help="Path to save sampled point cloud as PLY (default: %(default)s).",
    )
    parser.add_argument(
        "--copy-point-cloud",
        type=Path,
        default=DEFAULT_POINT_CLOUD_COPY,
        help="Optional extra PLY copy near raw data (default: %(default)s).",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Preview the sampled point cloud with Open3D (requires open3d).",
    )
    return parser.parse_args()


def _require_file(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Required input file not found: {path}")
    return path


def load_pointcloud(source_dir: Path, file_x: str, file_y: str, file_z: str) -> PointCloud:
    x = cv2.imread(str(_require_file(source_dir / file_x)), cv2.IMREAD_UNCHANGED)
    y = cv2.imread(str(_require_file(source_dir / file_y)), cv2.IMREAD_UNCHANGED)
    z = cv2.imread(str(_require_file(source_dir / file_z)), cv2.IMREAD_UNCHANGED)
    if x is None or y is None or z is None:
        raise RuntimeError("Unable to read one of the point cloud TIFF files.")
    if x.shape != y.shape or x.shape != z.shape:
        raise ValueError(f"Point cloud component shapes differ: {x.shape}, {y.shape}, {z.shape}")
    return PointCloud(
        x=x.astype(np.float32),
        y=y.astype(np.float32),
        z=z.astype(np.float32),
    )


def adjust_sampling(step: int, max_size: int, width: int, height: int) -> int:
    if step < 1:
        step = 1
    if max_size <= 0:
        return step
    sampled = math.ceil(width / step) * math.ceil(height / step)
    while sampled > max_size:
        step += 1
        sampled = math.ceil(width / step) * math.ceil(height / step)
    return step


def downsample_cloud(
    cloud: PointCloud,
    step: int,
    flip_y: bool,
    z_scale: float,
    epsilon: float,
) -> Tuple[np.ndarray, np.ndarray]:
    xs = cloud.x[::step, ::step]
    ys = cloud.y[::step, ::step]
    zs = cloud.z[::step, ::step] * z_scale

    if flip_y:
        ys = -ys

    stack = np.stack([xs, ys, zs], axis=-1)
    norms = np.linalg.norm(stack, axis=-1)
    valid_mask = norms > epsilon
    return stack, valid_mask


def compute_normals(grid: np.ndarray, valid_mask: np.ndarray) -> np.ndarray:
    height, width, _ = grid.shape
    normals = np.zeros_like(grid)

    for r in range(height):
        r_prev = max(0, r - 1)
        r_next = min(height - 1, r + 1)
        for c in range(width):
            c_prev = max(0, c - 1)
            c_next = min(width - 1, c + 1)

            if not valid_mask[r, c]:
                normals[r, c] = np.array([0.0, 0.0, 1.0], dtype=np.float32)
                continue

            v_center = grid[r, c]
            neighbors = [
                grid[r, c_next] - v_center,
                grid[r_next, c] - v_center,
                grid[r, c_prev] - v_center,
                grid[r_prev, c] - v_center,
            ]
            neighbor_mask = [
                valid_mask[r, c_next],
                valid_mask[r_next, c],
                valid_mask[r, c_prev],
                valid_mask[r_prev, c],
            ]
            normal = np.zeros(3, dtype=np.float32)
            for i in range(len(neighbors)):
                if not neighbor_mask[i] or not neighbor_mask[(i + 1) % len(neighbors)]:
                    continue
                v1 = neighbors[i]
                v2 = neighbors[(i + 1) % len(neighbors)]
                cross = np.cross(v1, v2)
                normal += cross
            norm = np.linalg.norm(normal)
            if norm > 1e-6:
                normals[r, c] = normal / norm
            else:
                normals[r, c] = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    return normals


def build_vertex_indices(valid_mask: np.ndarray) -> Tuple[np.ndarray, int]:
    height, width = valid_mask.shape
    indices = -np.ones_like(valid_mask, dtype=np.int32)
    counter = 0
    for r in range(height):
        for c in range(width):
            if valid_mask[r, c]:
                indices[r, c] = counter
                counter += 1
    return indices, counter


def iter_faces(index_grid: np.ndarray) -> Iterable[Tuple[int, int, int]]:
    height, width = index_grid.shape
    for r in range(height - 1):
        for c in range(width - 1):
            i0 = index_grid[r, c]
            i1 = index_grid[r, c + 1]
            i2 = index_grid[r + 1, c]
            i3 = index_grid[r + 1, c + 1]
            if i0 >= 0 and i2 >= 0 and i1 >= 0:
                yield (i0, i2, i1)
            if i2 >= 0 and i3 >= 0 and i1 >= 0:
                yield (i2, i3, i1)


def export_obj(path: Path, positions: np.ndarray, normals: np.ndarray, faces: Iterable[Tuple[int, int, int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        fh.write("# Generated by scripts/build_3d_model.py\n")
        fh.write(f"# Vertex count: {positions.shape[0]}\n")
        for pos in positions:
            fh.write(f"v {pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f}\n")
        for nrm in normals:
            fh.write(f"vn {nrm[0]:.6f} {nrm[1]:.6f} {nrm[2]:.6f}\n")
        for tri in faces:
            i0, i1, i2 = (idx + 1 for idx in tri)
            fh.write(f"f {i0}//{i0} {i1}//{i1} {i2}//{i2}\n")


def export_point_cloud(path: Path, positions: np.ndarray, normals: Optional[np.ndarray]) -> None:
    if not _O3D_AVAILABLE:
        raise RuntimeError("open3d is required for point cloud export. Install with `pip install open3d`.")
    path.parent.mkdir(parents=True, exist_ok=True)
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(positions.astype(np.float64))
    if normals is not None:
        point_cloud.normals = o3d.utility.Vector3dVector(normals.astype(np.float64))
    o3d.io.write_point_cloud(str(path), point_cloud, write_ascii=True)


def visualize_point_cloud(positions: np.ndarray, normals: Optional[np.ndarray]) -> None:
    if not _O3D_AVAILABLE:
        raise RuntimeError("open3d is required for visualization. Install with `pip install open3d`.")
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(positions.astype(np.float64))
    if normals is not None:
        point_cloud.normals = o3d.utility.Vector3dVector(normals.astype(np.float64))
    o3d.visualization.draw_geometries([point_cloud])


def main() -> None:
    args = parse_args()
    cloud = load_pointcloud(args.source_dir, args.file_x, args.file_y, args.file_z)
    height, width = cloud.shape

    step = adjust_sampling(args.step, args.max_size, width, height)
    sampled_grid, valid_mask = downsample_cloud(
        cloud,
        step=step,
        flip_y=args.flip_y,
        z_scale=args.z_scale,
        epsilon=args.valid_epsilon,
    )
    normals_grid = compute_normals(sampled_grid, valid_mask)
    index_grid, vertex_count = build_vertex_indices(valid_mask)

    if vertex_count == 0:
        raise RuntimeError("No valid points detected. Adjust --valid-epsilon or check input data.")

    positions = sampled_grid.reshape(-1, 3)[valid_mask.reshape(-1)]
    normals = normals_grid.reshape(-1, 3)[valid_mask.reshape(-1)]
    faces = list(iter_faces(index_grid))

    export_obj(args.output, positions, normals, faces)
    if args.copy_to:
        export_obj(args.copy_to, positions, normals, faces)

    print(f"Mesh written to {args.output.resolve()}")
    if args.copy_to:
        print(f"External copy written to {args.copy_to.resolve()}")

    if args.point_cloud:
        if _O3D_AVAILABLE:
            export_point_cloud(args.point_cloud, positions, normals)
            print(f"Point cloud written to {args.point_cloud.resolve()}")
            if args.copy_point_cloud:
                export_point_cloud(args.copy_point_cloud, positions, normals)
                print(f"External point cloud copy written to {args.copy_point_cloud.resolve()}")
        else:
            print("open3d not installed; skipping point cloud export.")

    if args.show:
        visualize_point_cloud(positions, normals)


if __name__ == "__main__":
    main()
