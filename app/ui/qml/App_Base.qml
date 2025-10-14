import QtQuick.Controls.Material
import QtQuick.Window
import "cores" as Cores

ApplicationWindow  {
  // Bind Material palette from coreStyle
  Material.theme: Material.Dark
  Material.primary: Cores.CoreStyle.primary
  Material.accent: Cores.CoreStyle.accent
  Material.background: Cores.CoreStyle.background
  Material.foreground: Cores.CoreStyle.text
  visibility:Window.Maximized
  visible: true

  width: Screen.width*0.8
  height: Screen.height*0.8

  title: Cores.Core.title
}



