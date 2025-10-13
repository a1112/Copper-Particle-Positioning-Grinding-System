from __future__ import annotations

from typing import Any

from fastapi import Response

import CONFIG
from ..api_core import image_router as router

_override_png = CONFIG.testFolder / "images" / "1_IMG_Texture_8Bit.png"
provider: Any | None = None  # injected by bootstrap


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
