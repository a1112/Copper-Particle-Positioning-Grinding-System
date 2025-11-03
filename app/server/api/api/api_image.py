from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple

from fastapi import HTTPException, Response
from fastapi.responses import FileResponse

import mimetypes
from pathlib import Path
import threading

from ..api_core import image_router as router

IMAGE_BASE_DIR = Path(r"D:\SaveData\current")
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
_point_cloud_cache: Dict[str, Any] = {}
_point_cloud_mtime: Dict[str, float] = {}
_point_cloud_shape: Tuple[int, int] | None = None
_point_cloud_lock = threading.Lock()


def _get_point_cloud_component(axis: str):
    axis_lower = (axis or "").lower()
    path = _POINT_CLOUD_FILENAMES.get(axis_lower)
    if path is None:
        raise HTTPException(status_code=404, detail="Unsupported point cloud axis")

    with _point_cloud_lock:
        if not path.exists():
            _point_cloud_cache.pop(axis_lower, None)
            _point_cloud_mtime.pop(axis_lower, None)
            raise HTTPException(status_code=404, detail=f"Point cloud source '{path.name}' missing")

        mtime = path.stat().st_mtime
        cached = _point_cloud_cache.get(axis_lower)
        if cached is not None and _point_cloud_mtime.get(axis_lower) == mtime:
            return cached

        try:
            import cv2
            import numpy as np
        except Exception as exc:  # pragma: no cover - dependency missing
            raise HTTPException(status_code=500, detail="Point cloud support unavailable") from exc

        data = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if data is None:
            raise HTTPException(status_code=500, detail=f"Failed to load point cloud component '{path.name}'")
        if data.ndim >= 3:
            data = data[:, :, 0]
        if data.dtype != np.float32:
            data = data.astype(np.float32, copy=False)

        shape = data.shape[:2]
        global _point_cloud_shape
        if _point_cloud_shape is None:
            _point_cloud_shape = shape
        elif _point_cloud_shape != shape:
            raise HTTPException(status_code=500, detail="Point cloud component dimensions mismatch")

        _point_cloud_cache[axis_lower] = data
        _point_cloud_mtime[axis_lower] = mtime
        return data


def _sample_point_cloud_pixel(x: int, y: int) -> Dict[str, float]:
    try:
        data_x = _get_point_cloud_component("x")
        data_y = _get_point_cloud_component("y")
        data_z = _get_point_cloud_component("z")
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="Point cloud cache unavailable") from exc

    height, width = data_x.shape[:2]
    if not (0 <= x < width and 0 <= y < height):
        raise HTTPException(status_code=400, detail="Pixel coordinates out of bounds")

    return {
        "x": float(data_x[y, x]),
        "y": float(data_y[y, x]),
        "z": float(data_z[y, x]),
    }


def _resolve_test_image(image_type: str) -> Tuple[Path, str]:
    key = (image_type or "").strip()
    if not key:
        key = "color"

    canonical = _IMAGE_TYPE_ALIASES.get(key) or _IMAGE_TYPE_ALIASES.get(key.lower())
    if canonical is None:
        raise HTTPException(status_code=404, detail="Unsupported image type")

    candidates: Iterable[str] = _IMAGE_FILE_CANDIDATES.get(canonical, ())
    if not IMAGE_BASE_DIR.exists():
        raise HTTPException(status_code=404, detail="Image directory not found")

    for candidate in candidates:
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
async def vision_pointcloud_pixel(x: int, y: int) -> Dict[str, Any]:
    sample = _sample_point_cloud_pixel(int(x), int(y))
    return {
        "pixel": {"x": int(x), "y": int(y)},
        "camera": sample,
    }


@router.get("/image/test")
async def image_test(type: str = "color") -> FileResponse:
    path, media_type = _resolve_test_image(type)
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
