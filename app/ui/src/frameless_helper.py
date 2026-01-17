"""
无边框窗口Windows Aero Snap支持

为无边框窗口添加Windows原生拖拽区域，使Aero Snap功能正常工作。
"""

import sys
import ctypes
import ctypes.wintypes
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QWindow

try:
    from PySide6.QtCore import QNativeEventFilter as _NativeEventFilterBase
except ImportError:  # Qt6 uses QAbstractNativeEventFilter in some builds
    from PySide6.QtCore import QAbstractNativeEventFilter as _NativeEventFilterBase


# Windows API 常量
WM_NCHITTEST = 0x0084
HTCLIENT = 1
HTCAPTION = 2

# Windows MSG 结构体（用于消息解析）
class MSG(ctypes.Structure):
    if sys.maxsize > 2**32:  # 64位
        _fields_ = [
            ("hwnd", ctypes.c_voidp),
            ("message", ctypes.c_uint),
            ("wParam", ctypes.c_size_t),
            ("lParam", ctypes.c_longlong),
            ("time", ctypes.c_uint32),
            ("pt", ctypes.c_voidp),  # POINT*
        ]
    else:  # 32位
        _fields_ = [
            ("hwnd", ctypes.c_voidp),
            ("message", ctypes.c_uint),
            ("wParam", ctypes.c_size_t),
            ("lParam", ctypes.c_long),
            ("time", ctypes.c_uint32),
            ("pt", ctypes.c_voidp),  # POINT*
        ]


class FramelessWindowsEventFilter(_NativeEventFilterBase):
    """
    Windows平台原生事件过滤器，用于支持无边框窗口的Aero Snap功能。

    原理：拦截WM_NCHITTEST消息，当鼠标在顶部区域时返回HTCAPTION，
    让Windows认为用户正在拖拽标题栏，从而触发Aero Snap。
    """

    def __init__(self, title_bar_height: int = 40):
        """
        Args:
            title_bar_height: 标题栏区域高度（像素），鼠标在此区域内拖拽会触发Aero Snap
        """
        super().__init__()
        self._title_bar_height = title_bar_height
        self._window: Optional[QWindow] = None

    def set_window(self, window: QWindow) -> None:
        """设置要处理的窗口"""
        self._window = window

    def set_title_bar_height(self, height: int) -> None:
        """设置标题栏区域高度"""
        self._title_bar_height = height

    def nativeEventFilter(
        self, eventType: bytes, message: bytes
    ) -> tuple[bool, int]:
        """
        原生事件过滤器

        Args:
            eventType: 事件类型
            message: 原生消息

        Returns:
            (是否已处理, 返回值)
        """
        # 仅处理Windows平台
        if eventType != b"windows_generic_MSG":
            return False, 0

        try:
            if self._window is None:
                return False, 0
            if not (self._window.flags() & Qt.FramelessWindowHint):
                return False, 0

            # 解析Windows MSG
            if isinstance(message, (bytes, bytearray)):
                msg = MSG.from_buffer_copy(message)
            else:
                msg = MSG.from_address(int(message))

            # 只处理WM_NCHITTEST消息
            if msg.message != WM_NCHITTEST:
                return False, 0

            # 检查是否是我们的窗口
            if self._window.winId() != msg.hwnd:
                return False, 0

            # lParam在WM_NCHITTEST中包含鼠标坐标
            # LOWORD(lParam) = x, HIWORD(lParam) = y (屏幕坐标)
            x = ctypes.c_short(msg.lParam & 0xFFFF).value
            y = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value

            # 将屏幕坐标转换为窗口客户区坐标
            point = ctypes.wintypes.POINT(x, y)
            ctypes.windll.user32.ScreenToClient(msg.hwnd, ctypes.byref(point))

            # 检查鼠标是否在顶部拖拽区域
            if 0 <= point.y < self._title_bar_height:
                # 返回HTCAPTION，让Windows认为在拖拽标题栏
                return True, HTCAPTION

        except Exception:
            pass

        return False, 0


# 全局事件过滤器实例
_global_filter: Optional[FramelessWindowsEventFilter] = None


def install_frameless_filter(window: QWindow, title_bar_height: int = 40) -> FramelessWindowsEventFilter:
    """
    为窗口安装无边框事件过滤器

    Args:
        window: 要处理的QWindow实例
        title_bar_height: 标题栏区域高度（像素）

    Returns:
        安装的事件过滤器实例
    """
    global _global_filter

    from PySide6.QtCore import QCoreApplication

    if _global_filter is None:
        _global_filter = FramelessWindowsEventFilter(title_bar_height)
        QCoreApplication.instance().installNativeEventFilter(_global_filter)
    else:
        _global_filter.set_title_bar_height(title_bar_height)

    _global_filter.set_window(window)
    return _global_filter


def set_frameless_drag_area(height: int) -> None:
    """
    设置无边框窗口的拖拽区域高度

    Args:
        height: 拖拽区域高度（像素），从窗口顶部开始计算
    """
    global _global_filter
    if _global_filter:
        _global_filter.set_title_bar_height(height)
