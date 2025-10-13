from fastapi.openapi.models import Response
import CONFIG
from ..api_core import app

_override_png = CONFIG.testFolder / "images" / "1_IMG_Texture_8Bit.png"

@app.get("/image.png")
async def image_png():
    # Prefer a bundled test image when present

    try:
        if _override_png.exists():
            return Response(content=_override_png.read_bytes(), media_type='image/png')
    except Exception:
        pass
    # Else encode current frame to PNG using OpenCV (pure backend)
    import numpy as np
    import cv2
    with provider._lock:  # type: ignore[attr-defined]
        frame = getattr(provider, "_frame_bgr", None)
        if frame is None:
            # Gray fallback image
            h, w = 360, 640
            gray = np.full((h, w, 3), 0x20, dtype=np.uint8)
            ok, buf = cv2.imencode(".png", gray)
            return Response(content=buf.tobytes() if ok else b"", media_type="image/png")
        else:
            ok, buf = cv2.imencode(".png", frame)
            return Response(content=buf.tobytes() if ok else b"", media_type="image/png")

@app.get("/image.png")
async def image_png():
    # If override test image exists, return its bytes
    try:
        if _override_png.exists():
            return Response(content=_override_png.read_bytes(), media_type='image/png')
    except Exception:
        pass
    # Else return current frame as PNG; gray fallback if empty
    from PySide6.QtGui import QImage
    from PySide6.QtCore import QByteArray, QBuffer
    with provider._lock:  # type: ignore[attr-defined]
        img = provider._img  # type: ignore[attr-defined]
        if img is None:
            image = QImage(640, 360, QImage.Format_RGB888)
            image.fill(0x202020)
            qba = QByteArray()
            buf = QBuffer(qba)
            buf.open(QBuffer.WriteOnly)
            image.save(buf, 'PNG')
            return Response(content=bytes(qba), media_type='image/png')
        else:
            qba = QByteArray()
            buf = QBuffer(qba)
            buf.open(QBuffer.WriteOnly)
            img.save(buf, 'PNG')
            return Response(content=bytes(qba), media_type='image/png')