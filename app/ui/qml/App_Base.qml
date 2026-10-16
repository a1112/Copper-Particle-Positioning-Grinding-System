import QtCore
import QtQuick
import QtQuick.Controls.Material
import QtQuick.Window
import "cores" as Cores
import "dialogs"
import "works" as Works
import "datas" as Datas

ApplicationWindow {

    // Screen dimensions are Qt logical pixels; do not multiply by devicePixelRatio.
    property bool startupGeometryReady: false
    Settings {
        id: startupGeometry
        category: "MainWindowGeometry"
        // Explicit isolated profile for automated/synthetic window smoke tests.
        location: {
            var prefix = "--window-geometry-settings="
            for (var i = 0; i < Qt.application.arguments.length; ++i) {
                var argument = Qt.application.arguments[i]
                if (argument.indexOf(prefix) === 0) return argument.substring(prefix.length)
            }
            return ""
        }
        property real savedX: -100000
        property real savedY: -100000
        property real savedWidth: 0
        property real savedHeight: 0
    }
    function fitStartupGeometry(useSaved) {
        var screens = Qt.application.screens
        var target = screen
        var px = useSaved ? startupGeometry.savedX : x
        var py = useSaved ? startupGeometry.savedY : y
        var pw = useSaved ? startupGeometry.savedWidth : width
        var ph = useSaved ? startupGeometry.savedHeight : height
        var saved = pw > 0 && ph > 0 && isFinite(px) && isFinite(py) && isFinite(pw) && isFinite(ph)
        var bestArea = 0
        for (var i = 0; i < screens.length; ++i) {
            var candidate = screens[i]
            var overlap = Math.max(0, Math.min(px + pw, candidate.virtualX + candidate.width) - Math.max(px, candidate.virtualX))
                * Math.max(0, Math.min(py + ph, candidate.virtualY + candidate.height) - Math.max(py, candidate.virtualY))
            if (overlap > bestArea) { target = candidate; bestArea = overlap }
        }
        if (!target) return
        screen = target
        // Reserve desktop edges and titlebar space in addition to the work-area limit.
        var aw = Math.max(1, Math.min(target.width, target.desktopAvailableWidth) - 48)
        var ah = Math.max(1, Math.min(target.height, target.desktopAvailableHeight) - 64)
        var left = target.virtualX + (target.width - aw) / 2
        var top = target.virtualY + (target.height - ah) / 2
        minimumWidth = Math.min(800, aw, saved && pw >= 320 ? pw : 800)
        minimumHeight = Math.min(520, ah, saved && ph >= 240 ? ph : 520)
        if (useSaved && !saved) {
            pw = Math.min(1100, Math.floor(aw * 0.82))
            ph = Math.min(720, Math.floor(ah * 0.82))
            px = left + (aw - pw) / 2
            py = top + (ah - ph) / 2
        }
        if (saved && px >= target.virtualX && py >= target.virtualY
                && px + pw <= target.virtualX + target.width
                && py + ph <= target.virtualY + target.height
                && pw <= target.desktopAvailableWidth && ph <= target.desktopAvailableHeight) {
            width = pw; height = ph; x = px; y = py
            return
        }
        width = Math.min(Math.max(pw, minimumWidth), aw)
        height = Math.min(Math.max(ph, minimumHeight), ah)
        x = Math.max(left, Math.min(px, left + aw - width))
        y = Math.max(top, Math.min(py, top + ah - height))
    }
    onScreenChanged: if (startupGeometryReady && visibility === Window.Windowed) fitStartupGeometry(false)
    onClosing: {
        if (visibility === Window.Windowed) {
            startupGeometry.savedX = x
            startupGeometry.savedY = y
            startupGeometry.savedWidth = width
            startupGeometry.savedHeight = height
        }
    }

  // main window
  id: rootWindow
  property real baseFontPointSize: Qt.application.font.pointSize > 0 ? Qt.application.font.pointSize : 12

  Connections {
    target: Cores.CoreSettings
    function onFontScaleChanged() {
      rootWindow.applyFontScale();
    }
  }
  // 采用暗色主题方案
  Material.theme: Material.Dark
  // 主色调取自 CoreStyle
  Material.primary: Cores.CoreStyle.primary
  // 强调色取自 CoreStyle
  Material.accent: Cores.CoreStyle.accent
  // 窗口背景色
  Material.background: Cores.CoreStyle.background
  // 文字前景色
  Material.foreground: Cores.CoreStyle.text
  // 默认最大化显示

    visibility: Window.Windowed
  // 窗口可见
  visible: true

  readonly property int normalWindowFlags: Qt.Window
  readonly property int framelessWindowFlags: Qt.Window
    | Qt.FramelessWindowHint
    | Qt.WindowSystemMenuHint
    | Qt.WindowMinimizeButtonHint
    | Qt.WindowMaximizeButtonHint
    | Qt.WindowCloseButtonHint
  property bool framelessEnabled: Cores.CoreSettings ? Cores.CoreSettings.framelessWindow : false

  function applyWindowFlags() {
    var targetFlags = framelessEnabled ? framelessWindowFlags : normalWindowFlags
    if (flags === targetFlags)
      return
    var wasFullScreen = visibility === Window.FullScreen
    var wasMaximized = visibility === Window.Maximized
    flags = targetFlags
    if (wasFullScreen) {
      showFullScreen()
    } else if (wasMaximized) {
      showMaximized()
    } else {
      showNormal()
    }
  }

  property int restoreVisibility: Window.Windowed
  function toggleFullScreen() {
    if (visibility === Window.FullScreen) {
      if (restoreVisibility === Window.Maximized) {
        showMaximized()
      } else {
        showNormal()
      }
      return
    }
    restoreVisibility = visibility
    showFullScreen()
  }

  Component.onCompleted: { fitStartupGeometry(true); startupGeometryReady = true; applyWindowFlags() }
  onFramelessEnabledChanged: applyWindowFlags()

  // 默认宽度为屏幕 80%

    width: 1100
  // 默认高度为屏幕 80%

    height: 720

  // 窗口标题
  title: Cores.CoreUI.title
  // Window icon configured via QGuiApplication in app.ui.main


}
