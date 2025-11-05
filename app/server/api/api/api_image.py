from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Tuple

from fastapi import HTTPException, Query, Response
from fastapi.responses import FileResponse

import mimetypes
from pathlib import Path
from ..api_core import image_router as router
from app import config
from app.server.data.pointcloud_cache import PointCloudCache, PointCloudError

IMAGE_BASE_DIR = config.SAVE_DATA_CURRENT_DIR
_override_png = IMAGE_BASE_DIR / "src_IMG_Texture_8Bit.png"

_IMAGE_FILE_CANDIDATES: Dict[str, Tuple[str, ...]] = {
    "color": ("src_IMG_Color.png", "src_IMG_Texture_8Bit.png"),
    "gray": ("src_IMG_Texture_8Bit.png", "rts_ImageZ1ZeroReal.tif", "rts_ImageSubZ1.tif"),
    "depth": (
        "rts_Z1.tif",
        "rts_ImageZ1ZeroReal.tif",
        "src_IMG_PointCloud_Z.tif",
    ),
    "normal": (
        "rts_NzRender.png",
        "src_IMG_NormalMap_Z.tif",
        "rts_ZTbRender.png",
    ),
}

_IMAGE_TYPE_ALIASES: Dict[str, str] = {
    "color": "color",
    "gray": "gray",
    "depth": "depth",
    "normal": "normal",
    "彩色": "color",
    "灰度": "gray",
    "深度": "depth",
    "法线": "normal",
}
provider: Any | None = None  # injected by bootstrap
_MASK_FILENAME = "rts_ImageZ1ZeroReal.tif"

_POINT_CLOUD_FILENAMES: Dict[str, Path] = {
    "x": IMAGE_BASE_DIR / "src_IMG_PointCloud_X.tif",
    "y": IMAGE_BASE_DIR / "src_IMG_PointCloud_Y.tif",
    "z": IMAGE_BASE_DIR / "src_IMG_PointCloud_Z.tif",
}
_point_cloud_cache = PointCloudCache(
    current_dir=config.SAVE_DATA_CURRENT_DIR,
    records_dir=config.SAVE_DATA_RECORDS_DIR,
    filenames=_POINT_CLOUD_FILENAMES,
)


def _sample_point_cloud_pixel(x: int, y: int, record_id: Optional[int] = None) -> Dict[str, float]:
    try:
        bundle = _point_cloud_cache.get_bundle(record_id)
    except PointCloudError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    data_x = bundle.arrays["x"]
    data_y = bundle.arrays["y"]
    data_z = bundle.arrays["z"]

    height, width = bundle.shape
    if not (0 <= x < width and 0 <= y < height):
        raise HTTPException(status_code=400, detail="Pixel coordinates out of bounds")

    return {
        "x": float(data_x[y, x]),
        "y": float(data_y[y, x]),
        "z": float(data_z[y, x]),
    }


def _lookup_point_cloud_camera(
    x: float,
    y: float,
    z: float | None = None,
    max_radius: float | None = None,
    record_id: Optional[int] = None,
) -> Dict[str, Any]:
    try:
        import numpy as np

        bundle = _point_cloud_cache.get_bundle(record_id)
    except PointCloudError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise HTTPException(status_code=500, detail="Point cloud cache unavailable") from exc

    data_x = bundle.arrays["x"]
    data_y = bundle.arrays["y"]
    data_z = bundle.arrays["z"]

    if not np.isfinite(x) or not np.isfinite(y):
        raise HTTPException(status_code=400, detail="Camera coordinates must be finite")

    target_x = float(x)
    target_y = float(y)
    target_z = float(z) if z is not None else None

    dx = data_x - target_x
    dy = data_y - target_y
    dist_sq = dx * dx + dy * dy

    if target_z is not None:
        dz = data_z - target_z
        dist_sq = dist_sq + dz * dz

    index = int(np.argmin(dist_sq))
    rows, cols = data_x.shape[:2]
    row, col = divmod(index, cols)

    best_dist_sq = float(dist_sq[row, col])
    best_dist = float(np.sqrt(best_dist_sq))

    if max_radius is not None and best_dist > float(max_radius):
        raise HTTPException(status_code=404, detail="No point within specified radius")

    result_pixel = {"x": int(col), "y": int(row)}
    result_camera = {
        "x": float(data_x[row, col]),
        "y": float(data_y[row, col]),
        "z": float(data_z[row, col]),
    }
    return {
        "pixel": result_pixel,
        "camera": result_camera,
        "distance": best_dist,
    }


def _resolve_test_image(image_type: str, variant: str | None = None) -> Tuple[Path, str]:
    key = (image_type or "").strip()
    if not key:
        key = "color"

    canonical = _IMAGE_TYPE_ALIASES.get(key) or _IMAGE_TYPE_ALIASES.get(key.lower())
    if canonical is None:
        raise HTTPException(status_code=404, detail="Unsupported image type")

    candidates: Iterable[str] = _IMAGE_FILE_CANDIDATES.get(canonical, ())
    candidates_list = list(candidates)
    variant_norm = (variant or "").strip().lower()

    if variant_norm == "src":
        src_first = [item for item in candidates_list if item.lower().startswith("src_")]
        others = [item for item in candidates_list if item not in src_first]
        candidates_list = src_first + others
    else:
        rts_first = [item for item in candidates_list if item.lower().startswith("rts_")]
        others = [item for item in candidates_list if item not in rts_first]
        if variant_norm == "rts" or not variant_norm:
            candidates_list = rts_first + others
        else:
            candidates_list = rts_first + others

    if not IMAGE_BASE_DIR.exists():
        raise HTTPException(status_code=404, detail="Image directory not found")

    for candidate in candidates_list:
        path = IMAGE_BASE_DIR / candidate
        if path.exists():
            media_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
            return path, media_type

    raise HTTPException(status_code=404, detail="Test image not found")


def _best_available_png() -> Path | None:
    if _override_png.exists():
        return _override_png
    gray_candidates = _IMAGE_FILE_CANDIDATES.get("gray", ())
    for candidate in gray_candidates:
        path = IMAGE_BASE_DIR / candidate
        if path.exists() and path.suffix.lower() == ".png":
            return path
    color_candidates = _IMAGE_FILE_CANDIDATES.get("color", ())
    for candidate in color_candidates:
        path = IMAGE_BASE_DIR / candidate
        if path.exists() and path.suffix.lower() == ".png":
            return path
    return None


def _load_png_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except Exception:
        return b""


def _generate_particle_mask_png() -> bytes:
    import numpy as np
    import cv2

    target_path = IMAGE_BASE_DIR / _MASK_FILENAME
    if not target_path.exists():
        return b""

    try:
        raw = cv2.imread(str(target_path), cv2.IMREAD_UNCHANGED)
        if raw is None:
            return b""
        if raw.ndim == 3:
            raw = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY)
        data = raw.astype(np.float32)
        mask = data > 0.0
        if not np.any(mask):
            height, width = data.shape[:2]
            transparent = np.zeros((height, width, 4), dtype=np.uint8)
            ok, buf = cv2.imencode(".png", transparent)
            return buf.tobytes() if ok else b""

        valid_values = data[mask]
        min_val = float(valid_values.min())
        max_val = float(valid_values.max())
        if max_val <= min_val:
            scale = np.zeros_like(data, dtype=np.uint8)
            scale[mask] = 255
        else:
            normalized = (data - min_val) / (max_val - min_val)
            scale = np.zeros_like(data, dtype=np.uint8)
            scale[mask] = np.clip(normalized[mask] * 255.0, 0, 255).astype(np.uint8)

        colored = cv2.applyColorMap(scale, cv2.COLORMAP_TURBO)
        colored[~mask] = 0
        alpha = np.zeros(data.shape, dtype=np.uint8)
        alpha[mask] = 200
        bgra = cv2.cvtColor(colored, cv2.COLOR_BGR2BGRA)
        bgra[:, :, 3] = alpha

        ok, buf = cv2.imencode(".png", bgra, [cv2.IMWRITE_PNG_COMPRESSION, 3])
        return buf.tobytes() if ok else b""
    except Exception:
        return b""


@router.get("/vision/pointcloud/pixel")
async def vision_pointcloud_pixel(
    x: int,
    y: int,
    record_id: Optional[int] = Query(default=None),
) -> Dict[str, Any]:
    sample = _sample_point_cloud_pixel(int(x), int(y), record_id)
    return {
        "pixel": {"x": int(x), "y": int(y)},
        "camera": sample,
    }


@router.get("/vision/pointcloud/lookup")
async def vision_pointcloud_lookup(
    x: float,
    y: float,
    z: float | None = None,
    max_radius: float | None = None,
    record_id: Optional[int] = Query(default=None),
) -> Dict[str, Any]:
    result = _lookup_point_cloud_camera(x, y, z, max_radius, record_id)
    return result


@router.get("/image/test")
async def image_test(type: str = "color", variant: str | None = None) -> FileResponse:
    path, media_type = _resolve_test_image(type, variant)
    return FileResponse(str(path), media_type=media_type, filename=path.name)


@router.get("/image.png")
async def image_png() -> Response:
    # Prefer a bundled test image when present
    override_path = _best_available_png()
    if override_path is not None:
        buf_bytes = _load_png_bytes(override_path)
        if buf_bytes:
            return Response(content=buf_bytes, media_type="image/png")

    import numpy as np
    import cv2

    buf_bytes = b""
    if provider is not None:
        with provider._lock:  # type: ignore[attr-defined]
            frame = getattr(provider, "_frame_bgr", None)
        if frame is not None:
            ok, buf = cv2.imencode(".png", frame)
            buf_bytes = buf.tobytes() if ok else b""

    if not buf_bytes:
        h, w = 360, 640
        gray = np.full((h, w, 3), 0x20, dtype=np.uint8)
        ok, buf = cv2.imencode(".png", gray)
        buf_bytes = buf.tobytes() if ok else b""

    return Response(content=buf_bytes, media_type="image/png")


@router.get("/image/mask")
async def image_mask() -> Response:
    buf = _generate_particle_mask_png()
    if not buf:
        raise HTTPException(status_code=404, detail="Particle mask image unavailable")
    return Response(content=buf, media_type="image/png")
