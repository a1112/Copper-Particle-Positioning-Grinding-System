from __future__ import annotations

from typing import Any, Dict, Tuple

from fastapi import HTTPException, Response
from fastapi.responses import FileResponse

import mimetypes
from pathlib import Path

import app.config as CONFIG
from ..api_core import image_router as router

_override_png = CONFIG.testFolder / "images" / "1_IMG_Texture_8Bit.png"
_TEST_IMAGE_FILES: Dict[str, str] = {
    "color": "0_IMG_Color.png",
    "gray": "0_IMG_Texture_8Bit.png",
    "depth": "1_Z1.tif",
    "normal": "1_NzRender.png",
}
_TEST_IMAGE_ALIASES: Dict[str, str] = {
    **_TEST_IMAGE_FILES,
    "彩色": _TEST_IMAGE_FILES["color"],
    "灰度": _TEST_IMAGE_FILES["gray"],
    "深度": _TEST_IMAGE_FILES["depth"],
    "法线": _TEST_IMAGE_FILES["normal"],
}
provider: Any | None = None  # injected by bootstrap


def _resolve_test_image(image_type: str) -> Tuple[Path, str]:
    key = (image_type or "").strip()
    if not key:
        key = "color"
    filename = _TEST_IMAGE_ALIASES.get(key) or _TEST_IMAGE_ALIASES.get(key.lower())
    if filename is None:
        raise HTTPException(status_code=404, detail="Unsupported image type")
    path = CONFIG.testFolder / "images" / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Test image not found")
    media_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return path, media_type


@router.get("/image/test")
async def image_test(type: str = "color") -> FileResponse:
    path, media_type = _resolve_test_image(type)
    return FileResponse(str(path), media_type=media_type, filename=path.name)


@router.get("/image.png")
async def image_png() -> Response:
    # Prefer a bundled test image when present
    try:
        if _override_png.exists():
            return Response(content=_override_png.read_bytes(), media_type="image/png")
    except Exception:
        pass

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
