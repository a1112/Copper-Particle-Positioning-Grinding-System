from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Sequence

import cv2
import numpy as np

from .config import TaskConfig
from .models import Fixture, PipelineResult


def _serialize_fixture(fixture: Fixture) -> Dict[str, object]:
    """将单个夹具对象转成可序列化字典。"""
    return {
        "id": fixture.id,
        "centroid": list(map(float, fixture.centroid_xy)),
        "area_mm2": float(fixture.area_mm2),
        "max_height": float(fixture.max_height),
        "radius_mm": float(fixture.radius_mm),
    }


def export_summary(result: PipelineResult, config: TaskConfig, destination: Path) -> Path:
    """导出汇总 JSON、基面及切削路径等核心文件。"""
    destination.parent.mkdir(parents=True, exist_ok=True)
    xs = result.cloud.xs[result.board_mask]
    ys = result.cloud.ys[result.board_mask]
    board_extent = {
        "x": [float(xs.min()), float(xs.max())],
        "y": [float(ys.min()), float(ys.max())],
    }
    payload = {
        "config": config.to_dict(),
        "plane": {
            "normal": result.plane.normal.tolist(),
            "offset": result.plane.offset,
            "rms_error": result.plane.rms_error,
            "inlier_ratio": result.plane.inlier_ratio,
        },
        "board": {
            "height": result.board_height,
            "extent_mm": board_extent,
        },
        "fixtures": [_serialize_fixture(fixture) for fixture in result.fixtures],
        "particles": [
            {
                "id": particle.id,
                "centroid": list(map(float, particle.centroid_xy)),
                "max_height": float(particle.max_height),
                "mean_height": float(particle.mean_height),
                "area_mm2": float(particle.area_mm2),
                "density": float(particle.density),
                "orientation": particle.orientation,
            }
            for particle in result.particles
        ],
    }
    cut_segments = [segment for segment in result.toolpaths.segments if segment.kind == "cut"]
    cut_array = np.empty((len(cut_segments), 9), dtype=np.float32)
    for idx, segment in enumerate(cut_segments):
        cut_array[idx, 0:3] = segment.start
        cut_array[idx, 3:6] = segment.end
        cut_array[idx, 6] = segment.feed_rate
        cut_array[idx, 7] = float(segment.cluster_id)
        cut_array[idx, 8] = float(segment.pass_index)
    cut_path = destination.with_name("cut_segments.npy")
    np.save(cut_path, cut_array)
    kind_map = {"rapid": 0, "plunge": 1, "cut": 2, "retract": 3}
    path_vertices: list[list[float]] = []
    for segment in result.toolpaths.segments:
        kind_code = float(kind_map.get(segment.kind, -1))
        path_vertices.append(
            [
                float(segment.start[0]),
                float(segment.start[1]),
                float(segment.start[2]),
                float(segment.feed_rate),
                float(segment.cluster_id),
                float(segment.pass_index),
                kind_code,
            ]
        )
    if result.toolpaths.segments:
        last = result.toolpaths.segments[-1]
        kind_code = float(kind_map.get(last.kind, -1))
        path_vertices.append(
            [
                float(last.end[0]),
                float(last.end[1]),
                float(last.end[2]),
                float(last.feed_rate),
                float(last.cluster_id),
                float(last.pass_index),
                kind_code,
            ]
        )
    path_array = np.array(path_vertices, dtype=np.float32)
    path_file = destination.with_name("spindle_path.npy")
    np.save(path_file, path_array)
    payload["toolpaths"] = {
        "total_segments": len(result.toolpaths.segments),
        "cut_segment_count": len(cut_segments),
        "cut_segments_file": cut_path.name,
        "spindle_path_file": path_file.name,
    }
    with destination.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    cv2.imwrite(
        str(destination.with_name("base_height_map.tif")),
        result.base_height_map.astype(np.float32),
    )
    # 保存“高于平面+余量(默认1.5mm)”的高度图（仅保留超出部分，其他置0）
    # 平面使用 pipeline 估计的板面高度 result.board_height
    height_above_plane = (float(result.board_height) - result.z_image_full).astype(np.float32)
    valid_mask = (result.z_image_full > 0)
    height_above_plane[~valid_mask] = 0.0
    # 阈值采用配置中的 finish_allowance（默认 1.5mm）
    threshold = float(config.finish_allowance)
    height_above_plane = np.clip(height_above_plane - threshold, 0.0, None)
    cv2.imwrite(
        str(destination.with_name("height_above_base.tif")),
        height_above_plane,
    )
    return destination


def export_visuals(output_dir: Path, visuals: Dict[str, object]) -> Dict[str, Sequence[Path]]:
    """根据可视化字典写出 PNG/TIF 资源，返回实际生成的文件路径。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    written: Dict[str, Sequence[Path]] = {}
    for key, value in visuals.items():
        if key == "frames":
            paths = []
            frames: Sequence[np.ndarray] = value  # type: ignore[assignment]
            for idx, frame in enumerate(frames):
                frame_path = output_dir / f"path_step_{idx:03d}.png"
                cv2.imwrite(str(frame_path), frame)
                paths.append(frame_path)
            written[key] = paths
        else:
            frame = value  # type: ignore[assignment]
            if isinstance(frame, np.ndarray):
                if key == "z_without_fixtures":
                    tif_path = output_dir / "z_without_fixtures.tif"
                    cv2.imwrite(str(tif_path), frame.astype(np.float32))
                    written[key] = [tif_path]
                elif key == "board_mask":
                    tif_path = output_dir / "board_mask.tif"
                    cv2.imwrite(str(tif_path), frame.astype(np.float32))
                    written[key] = [tif_path]
                elif key == "particle_hsv" or key == "board_fixture_hsv" or key == "reference_hsv":
                    continue
                else:
                    frame_path = output_dir / f"{key}.png"
                    cv2.imwrite(str(frame_path), frame)
                    written[key] = [frame_path]
    return written
