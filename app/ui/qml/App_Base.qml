import QtQuick
import QtQuick.Controls.Material
import QtQuick.Window
import "cores" as Cores
import "action"
import "dialogs"
import "works" as Works
import "datas" as Datas

ApplicationWindow {
  // 主窗口对象
  id: rootWindow
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
  title: Cores.Core.title

  EstopDialog {
    id: estopDialog
  }

  Shortcuts {}
}
