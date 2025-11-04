from __future__ import annotations

import importlib.util
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional

import json
from shutil import copy2

from app import config


LOG = logging.getLogger("common.save_data")

ALLOWED_ARTIFACT_EXTENSIONS = {".tif", ".tiff", ".png", ".json"}

_records_root = config.SAVE_DATA_RECORDS_DIR
_current_dir = config.SAVE_DATA_CURRENT_DIR
_alg_result_source = config.SAVE_DATA_ALG_RESULT_PATH
_mesh_threads: Dict[int, threading.Thread] = {}
_mesh_threads_lock = threading.Lock()
_mesh_module = None
_mesh_module_lock = threading.Lock()


def ensure_records_root() -> Path:
    """Ensure the root record directory exists and return it."""
    _records_root.mkdir(parents=True, exist_ok=True)
    return _records_root


def ensure_record_folder(record_id: int) -> Path:
    """Return the folder for a record, creating it if needed."""
    folder = ensure_records_root() / str(record_id)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def folder_is_empty(folder: Path) -> bool:
    """Return True when the folder has no files."""
    try:
        next(folder.iterdir())
    except StopIteration:
        return True
    except FileNotFoundError:
        return True
    return False


def copy_current_artifacts(target_folder: Path) -> List[Path]:
    """Copy known capture artifacts from the current directory into the target folder."""
    copied: List[Path] = []
    if not _current_dir.exists():
        LOG.warning("SaveData current directory missing at %s; nothing to copy.", _current_dir)
        return copied

    for item in _current_dir.iterdir():
        if not item.is_file():
            continue
        if item.suffix.lower() not in ALLOWED_ARTIFACT_EXTENSIONS:
            continue
        destination = target_folder / item.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            copy2(item, destination)
        except Exception as exc:  # pragma: no cover - defensive logging
            LOG.warning("Failed to copy %s -> %s: %s", item, destination, exc)
            continue
        copied.append(destination)
    return copied


def copy_alg_result(target_folder: Path) -> tuple[Optional[Path], Optional[dict]]:
    """Copy alg_result.json into the record folder and return its path and parsed content."""
    if not _alg_result_source.exists():
        LOG.warning("Algorithm result source missing at %s; skipping copy.", _alg_result_source)
        return None, None
    destination = target_folder / "alg_result.json"
    try:
        copy2(_alg_result_source, destination)
    except Exception as exc:  # pragma: no cover - defensive logging
        LOG.warning("Failed to copy alg_result.json %s -> %s: %s", _alg_result_source, destination, exc)
        return None, None
    try:
        with destination.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:  # pragma: no cover - defensive logging
        LOG.warning("Unable to parse alg_result.json at %s: %s", destination, exc)
        return destination, None
    return destination, data


def spawn_mesh_builder(record_id: int, record_folder: Path) -> None:
    """Kick off background mesh generation for the given record."""
    with _mesh_threads_lock:
        existing = _mesh_threads.get(record_id)
        if existing and existing.is_alive():
            return
        thread = threading.Thread(
            target=_mesh_worker,
            name=f"mesh-builder-{record_id}",
            args=(record_id, record_folder),
            daemon=True,
        )
        _mesh_threads[record_id] = thread
        thread.start()


def _mesh_worker(record_id: int, record_folder: Path) -> None:
    try:
        module = _load_mesh_module()
        if module is None:
            return
        if not _current_dir.exists():
            LOG.warning("Cannot build mesh for record %s; current directory missing at %s", record_id, _current_dir)
            return

        # Load structured-light point cloud
        cloud = module.load_pointcloud(_current_dir, module.DEFAULT_FILE_X, module.DEFAULT_FILE_Y, module.DEFAULT_FILE_Z)
        height, width = cloud.shape

        step = module.adjust_sampling(4, 600 * 600, width, height)
        sampled_grid, valid_mask = module.downsample_cloud(
            cloud,
            step=step,
            flip_y=False,
            z_scale=1.0,
            epsilon=1e-6,
        )
        normals_grid = module.compute_normals(sampled_grid, valid_mask)
        index_grid, vertex_count = module.build_vertex_indices(valid_mask)
        if vertex_count == 0:
            LOG.warning("No valid points detected while building mesh for record %s", record_id)
            return

        positions = sampled_grid.reshape(-1, 3)[valid_mask.reshape(-1)]
        normals = normals_grid.reshape(-1, 3)[valid_mask.reshape(-1)]

        center_offset: Optional[object] = None
        if hasattr(module, "center_positions"):
            positions, center_offset = module.center_positions(positions)

        faces = list(module.iter_faces(index_grid))

        obj_path = record_folder / "generated_surface.obj"
        module.export_obj(obj_path, positions, normals, faces)

        meta_path = record_folder / "generated_surface_meta.json"
        if hasattr(module, "write_metadata"):
            module.write_metadata(
                meta_path,
                center=center_offset,
                step=step,
                z_scale=1.0,
                epsilon=1e-6,
            )

        mesh_dir = record_folder / "meshes"
        mesh_dir.mkdir(parents=True, exist_ok=True)

        balsam_path = config.SAVE_DATA_BALSAM_PATH
        if balsam_path and balsam_path.exists():
            mesh_output = mesh_dir / "defaultobject_mesh.mesh"
            try:
                module.convert_with_balsam(balsam_path, obj_path, mesh_output)
            except RuntimeError as exc:  # pragma: no cover - external tool
                LOG.warning("Balsam conversion failed for record %s: %s", record_id, exc)
        else:
            LOG.debug("Skipping Balsam conversion for record %s; executable not configured.", record_id)
    except Exception as exc:  # pragma: no cover - robustness
        LOG.exception("Mesh generation failed for record %s: %s", record_id, exc)
    finally:
        with _mesh_threads_lock:
            _mesh_threads.pop(record_id, None)


def _load_mesh_module():
    global _mesh_module
    with _mesh_module_lock:
        if _mesh_module is not None:
            return _mesh_module
        script_path = config.PROJECT_ROOT / "scripts" / "build_3d_model.py"
        if not script_path.exists():
            LOG.warning("Mesh builder script missing at %s", script_path)
            return None
        spec = importlib.util.spec_from_file_location("build_3d_model", str(script_path))
        if spec is None or spec.loader is None:
            LOG.warning("Unable to load mesh builder script from %s", script_path)
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        _mesh_module = module
        return _mesh_module


__all__ = [
    "ALLOWED_ARTIFACT_EXTENSIONS",
    "copy_current_artifacts",
    "copy_alg_result",
    "ensure_record_folder",
    "ensure_records_root",
    "folder_is_empty",
    "spawn_mesh_builder",
]
