import QtQuick
import QtQuick.Controls.Material
import QtQuick.Window
import "cores" as Cores
import "dialogs"
import "works" as Works
import "datas" as Datas

ApplicationWindow {
  // main window
  id: rootWindow
  property real baseFontPointSize: Qt.application.font.pointSize > 0 ? Qt.application.font.pointSize : 12

  function applyFontScale() {
    const scale = Cores.CoreSettings ? Cores.CoreSettings.fontScale : 1.0;
    const base = baseFontPointSize > 0 ? baseFontPointSize : 12;
    Qt.application.font = Qt.font({ pointSize: base * scale });
  }

  Component.onCompleted: applyFontScale()

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
  visibility: Window.Maximized
  // 窗口可见
  visible: true

  // 默认宽度为屏幕 80%
  width: Screen.width*0.8
  // 默认高度为屏幕 80%
  height: Screen.height*0.8

  // 窗口标题
  title: Cores.CoreUI.title


}

