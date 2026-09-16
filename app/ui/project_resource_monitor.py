"""Application process-tree sampling and an optional Qt Quick monitor.

Sampling opens no network listener. CPU is normalized to machine capacity;
memory is summed RSS (shared pages may be counted more than once).
"""
import importlib
import os
import time
from concurrent.futures import ThreadPoolExecutor


class ResourceSampler:
    """Maintain baselines by PID and creation time, including current children."""

    def __init__(self) -> None:
        self._previous = {}
        self._sampled_at = None

    def sample(self) -> dict:
        """Return nullable metrics; never substitute zero for an unavailable metric."""
        try:
            import psutil
        except ImportError:
            return {"available": False, "reason": "需要安装 psutil 以读取应用资源"}
        now = time.monotonic()
        elapsed = now - self._sampled_at if self._sampled_at is not None else None
        root = psutil.Process(os.getpid())
        processes = [root] + root.children(recursive=True)
        current = {}
        cpu_delta = reads = writes = memory = 0
        partial = False
        io_available = True
        for process in processes:
            try:
                with process.oneshot():
                    identity = (process.pid, process.create_time())
                    cpu_time = process.cpu_times()
                    cpu = cpu_time.user + cpu_time.system
                    rss = process.memory_info().rss
                    try:
                        io = process.io_counters()
                        read, written = io.read_bytes, io.write_bytes
                    except (AttributeError, NotImplementedError, psutil.AccessDenied):
                        read = written = None
                        io_available = False
                memory += rss
                old = self._previous.get(identity)
                if old is not None:
                    cpu_delta += max(0, cpu - old[0])
                    if read is not None and old[1] is not None:
                        reads += max(0, read - old[1])
                        writes += max(0, written - old[2])
                current[identity] = (cpu, read, written)
            except psutil.NoSuchProcess:
                continue
            except psutil.AccessDenied:
                partial = True
        self._previous = current
        self._sampled_at = now
        baseline = elapsed is not None and elapsed > 0
        return {
            "available": bool(current),
            "cpu_percent": min(100.0, cpu_delta / elapsed / (psutil.cpu_count() or 1) * 100) if baseline else None,
            "memory_bytes": memory if current else None,
            "read_bytes_per_second": reads / elapsed if baseline and io_available else None,
            "write_bytes_per_second": writes / elapsed if baseline and io_available else None,
            "process_count": len(current), "partial": partial,
            "gpu_percent": None,
        }


def install(engine, widget=None) -> None:
    """Attach one monitor per Qt Quick window using the application's Qt binding."""
    binding = type(engine).__module__.split(".")[0]
    core = importlib.import_module(binding + ".QtCore")
    qml = importlib.import_module(binding + ".QtQml")
    quick = importlib.import_module(binding + ".QtQuick")
    values = qml.QQmlPropertyMap(engine)
    values.insert("summary", "资源监控 · 采样中")
    values.insert("details", "正在采样…")
    engine.rootContext().setContextProperty("projectResourceMonitor", values)
    panels = []
    components = []

    def attach(window, _url) -> None:
        if not isinstance(window, quick.QQuickWindow):
            return
        component = qml.QQmlComponent(engine)
        component.setData(_PANEL.encode("utf-8"), core.QUrl())
        panel = component.create(engine.rootContext())
        if panel is not None:
            qml.QQmlEngine.setObjectOwnership(panel, qml.QQmlEngine.CppOwnership)
            content = window.contentItem()
            qml.QQmlEngine.setObjectOwnership(content, qml.QQmlEngine.CppOwnership)
            panel.setParent(content)
            panel.setParentItem(content)
            panels.append(panel)
            components.append((component, window, content))

    if widget is None:
        engine.objectCreated.connect(attach)
    else:
        attach(widget.quickWindow(), core.QUrl())
        widget._project_resource_monitor_engine = engine
    sampler = ResourceSampler()
    executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="app-resource-monitor")
    pending = [None]
    timer = core.QTimer(engine)
    timer.setInterval(2000)

    def tick() -> None:
        visible = widget.isVisible() if widget is not None else any(
            isinstance(root, quick.QQuickWindow) and root.isVisible() and root.windowState() != core.Qt.WindowMinimized
            for root in engine.rootObjects())
        if not visible:
            return
        if pending[0] is not None and pending[0].done():
            try:
                metrics = pending[0].result()
                if not metrics["available"]:
                    raise RuntimeError(metrics.get("reason", "无法读取进程信息"))
                cpu = metrics["cpu_percent"]
                cpu_text = "采样中" if cpu is None else f"{cpu:.1f}%"
                values.insert("summary", f"CPU {cpu_text} · {metrics['memory_bytes'] / 1048576:.1f} MiB")
                def rate(key: str) -> str:
                    value = metrics[key]
                    return "不可用 / 等待基线" if value is None else f"{value / 1024:.1f} KiB/s"
                values.insert("details", f"读 {rate('read_bytes_per_second')} · 写 {rate('write_bytes_per_second')}\n"
                              f"{metrics['process_count']} 个进程 · GPU：不可用\n"
                              "本应用及子进程；CPU 按整机容量计，内存 RSS 求和可能含共享页。隐藏时暂停。"
                              + (" 部分进程权限不足。" if metrics["partial"] else ""))
            except Exception:
                values.insert("summary", "资源监控 · 暂不可用")
                values.insert("details", "采样失败；请检查 psutil 依赖及当前进程权限。")
            pending[0] = None
        if pending[0] is None:
            pending[0] = executor.submit(sampler.sample)

    timer.timeout.connect(tick)
    timer.start()
    def close() -> None:
        timer.stop()
        executor.shutdown(wait=False)
    core.QCoreApplication.instance().aboutToQuit.connect(close)
    engine._project_resource_monitor = (values, panels, sampler, executor, timer, tick, attach, close, components)


_PANEL = r'''import QtQuick 2.12
Rectangle {
    anchors.right: parent.right; anchors.bottom: parent.bottom
    anchors.margins: 12; z: 100000
    width: expanded ? 310 : label.implicitWidth + 20
    height: expanded ? 170 : 30; radius: 6; color: "#182334"; border.color: "#64748b"
    property bool expanded: false
    activeFocusOnTab: true
    Accessible.role: Accessible.Button
    Accessible.name: "Application resource monitor"
    Keys.onSpacePressed: expanded = !expanded
    Keys.onReturnPressed: expanded = !expanded
    Keys.onEscapePressed: expanded = false
    Text { id: label; x: 10; y: 6; color: "#eef2ff"; font.pixelSize: 12; text: projectResourceMonitor.summary }
    Text { x: 10; y: 32; width: parent.width - 20; visible: parent.expanded; color: "#eef2ff"; font.pixelSize: 12; wrapMode: Text.Wrap; text: projectResourceMonitor.details }
    MouseArea { anchors.fill: parent; onClicked: { parent.forceActiveFocus(); parent.expanded = !parent.expanded } }
}'''
