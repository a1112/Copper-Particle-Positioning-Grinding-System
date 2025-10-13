from __future__ import annotations
from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtGui import QImage
from threading import Lock
import numpy as np


class CameraImageProvider(QQuickImageProvider):
    """QML 图像提供者（中文注释）

    提供 `image://camera/...` 源的图像数据，内部维护最后一帧 QImage。
    """
    def __init__(self) -> None:
        super().__init__(QQuickImageProvider.Image)
        self._lock = Lock()
        self._img: QImage | None = None
        # Keep a copy of latest frame in BGR uint8 for backend encoding
        self._frame_bgr: np.ndarray | None = None

    def requestImage(self, id, size, requestedSize):  # type: ignore[override]
        """QML 请求图像回调（中文注释）。若暂无帧，则返回灰底图。"""
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
        """设置当前帧（中文注释）。

        期望输入：BGR 格式、uint8、形状 HxWx3。
        内部转换为 QImage 并保存拷贝。
        """
        # 期望 BGR uint8 HxWx3
        if frame is None or frame.ndim != 3 or frame.shape[2] != 3:
            return
        h, w, _ = frame.shape
        rgb = frame[:, :, ::-1].copy()
        img = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        with self._lock:
            self._img = img.copy()
            # Store a copy for server-side encoding (avoid sharing memory)
            try:
                self._frame_bgr = frame.copy()
            except Exception:
                self._frame_bgr = None
