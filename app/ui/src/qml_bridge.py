from PySide6.QtCore import QObject, Slot, Property, Signal, QUrl, QTimer
from typing import Optional
from app.core.comm import TcpClient, RetryPolicy, Protocol
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QByteArray, QBuffer
import numpy as np

class Backend(QObject):
    """QML 后端桥（中文注释）

    作用：向 QML 暴露运行状态、日志、相机帧与控制接口（运动/回零等）。
    """
    logsChanged = Signal()
    statusChanged = Signal()

    def __init__(self, orchestrator):
        super().__init__()
        self._logs = ""
        self._status = "Idle"
        self.orchestrator = orchestrator
        self._comm_client: Optional[TcpClient] = None
        self._comm_connected = False
        self._comm_log = ""
        self._pos_text = "X0 Y0 Z0 T0"
        self._lock_door = True
        self._lock_vacuum = True
        self._lock_estop = False
        self._lock_homed = True
        self._lock_spindle = True
        self._frame_url = ''
        self._last_frame = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(100)
        # vision results
        self._tx = -1.0
        self._ty = -1.0
        self._tth = 0.0
        self._tscore = 0.0

    @Property(str, notify=logsChanged)
    def logs(self):
        return self._logs

    @Property(str, notify=statusChanged)
    def status(self):
        return self._status

    @Property(bool, notify=statusChanged)
    def commConnected(self):
        return self._comm_connected

    @Property(str, notify=logsChanged)
    def commLog(self):
        return self._comm_log

    @Slot()
    def startRun(self):
        """开始运行（中文注释）。"""
        self._status = "Running"
        self.statusChanged.emit()

    @Slot()
    def stopRun(self):
        """停止运行（中文注释）。"""
        self._status = "Stopped"
        self.statusChanged.emit()

    @Slot(str, int)
    def toggleComm(self, host: str, port: int):
        """连接/断开与设备通讯（中文注释）。"""
        if self._comm_connected:
            try:
                assert self._comm_client
                self._comm_client.close()
            finally:
                self._comm_connected = False
        else:
            try:
                self._comm_client = TcpClient(host, port, timeout=2.0)
                self._comm_client.connect()
                self._comm_connected = True
                proto = Protocol()
                payload = proto.pack('PG', {'ts': 0})
                resp = self._comm_client.request(payload, RetryPolicy())
                self._comm_log += f"\nRESP {len(resp)} bytes"
            except Exception as e:
                self._comm_log += f"\nERR {e}"
                self._comm_connected = False
        self.statusChanged.emit()
        self.logsChanged.emit()

    @Property(str, notify=statusChanged)
    def posText(self):
        return self._pos_text

    @Slot(float, float)
    def setSpeed(self, vFast: float, vWork: float):
        """设置速度（中文注释）。"""
        if hasattr(self.orchestrator.motion, 'set_speed'):
            self.orchestrator.motion.set_speed(vFast, vWork)

    @Slot(str, int)
    def jog(self, axis: str, direction: int):
        """点动（中文注释）。"""
        if hasattr(self.orchestrator.motion, 'jog'):
            self.orchestrator.motion.jog(axis, direction, speed=10.0)
        if hasattr(self.orchestrator.motion, 'status'):
            x, y, z, t = self.orchestrator.motion.status()
            self._pos_text = f"X{x:.3f} Y{y:.3f} Z{z:.3f} T{t:.3f}"
            self.statusChanged.emit()

    @Slot()
    def home(self):
        """回零（中文注释）。"""
        if hasattr(self.orchestrator.motion, 'home'):
            self.orchestrator.motion.home()

    @Slot()
    def setWorkOrigin(self):
        """设置工件原点（中文注释）。"""
        if hasattr(self.orchestrator.motion, 'set_work_origin'):
            self.orchestrator.motion.set_work_origin()

    @Slot()
    def refresh(self):
        """刷新 UI（中文注释）。"""
        # Allow QML to request a UI refresh safely
        self.statusChanged.emit()

    @Property(bool, notify=statusChanged)
    def lockDoor(self):
        return self._lock_door

    @Property(bool, notify=statusChanged)
    def lockVacuum(self):
        return self._lock_vacuum

    @Property(bool, notify=statusChanged)
    def lockEStop(self):
        return self._lock_estop

    @Property(bool, notify=statusChanged)
    def lockHomed(self):
        return self._lock_homed

    @Property(bool, notify=statusChanged)
    def lockSpindle(self):
        return self._lock_spindle

    @Property(str, notify=statusChanged)
    def frameUrl(self):
        return self._frame_url

    def _tick(self):
        if getattr(self, '_last_frame', None) is None:
            img = QImage(640, 360, QImage.Format_RGB888)
            img.fill(0x202020)
            self._last_frame = img
        pix = QPixmap.fromImage(self._last_frame)
        qba = QByteArray()
        buf = QBuffer(qba)
        buf.open(QBuffer.WriteOnly)
        pix.save(buf, 'PNG')
        self._frame_url = f"data:image/png;base64,{bytes(qba.toBase64()).decode('ascii')}"
        self.statusChanged.emit()

    # Exposed for vision/camera callback to push numpy frames (H,W,3, uint8, BGR)
    @Slot()
    def clearFrame(self):
        """清空最后一帧（中文注释）。"""
        self._last_frame = None

    def push_numpy_frame(self, frame: np.ndarray):
        """推送 numpy 帧（中文注释）。期望 BGR/uint8/HxWx3。"""
        try:
            if frame is None or frame.ndim != 3 or frame.shape[2] != 3:
                return
            h, w, _ = frame.shape
            # Convert BGR->RGB
            rgb = frame[:, :, ::-1].copy()
            img = QImage(rgb.data, w, h, 3*w, QImage.Format_RGB888)
            self._last_frame = img.copy()
        except Exception:
            pass

    # vision result setters
    def set_target(self, x: float, y: float, theta: float, score: float):
        """设置视觉结果（中文注释）。"""
        self._tx, self._ty, self._tth, self._tscore = x, y, theta, score
        self.statusChanged.emit()

    @Property(float, notify=statusChanged)
    def targetX(self):
        return self._tx

    @Property(float, notify=statusChanged)
    def targetY(self):
        return self._ty

    @Property(float, notify=statusChanged)
    def targetTheta(self):
        return self._tth

    @Property(float, notify=statusChanged)
    def targetScore(self):
        return self._tscore
