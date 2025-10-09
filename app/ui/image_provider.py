from __future__ import annotations
from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtGui import QImage
from threading import Lock
import numpy as np


class CameraImageProvider(QQuickImageProvider):
    def __init__(self) -> None:
        super().__init__(QQuickImageProvider.Image)
        self._lock = Lock()
        self._img: QImage | None = None

    def requestImage(self, id, size, requestedSize):  # type: ignore[override]
        with self._lock:
            if self._img is None:
                img = QImage(640, 360, QImage.Format_RGB888)
                img.fill(0x202020)
                if size is not None:
                    size.setWidth(img.width())
                    size.setHeight(img.height())
                return img
            if size is not None:
                size.setWidth(self._img.width())
                size.setHeight(self._img.height())
            return self._img

    def set_frame(self, frame: np.ndarray) -> None:
        # Expect BGR uint8 HxWx3
        if frame is None or frame.ndim != 3 or frame.shape[2] != 3:
            return
        h, w, _ = frame.shape
        rgb = frame[:, :, ::-1].copy()
        img = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        with self._lock:
            self._img = img.copy()
