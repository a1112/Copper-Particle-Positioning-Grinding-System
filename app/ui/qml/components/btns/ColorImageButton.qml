import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtGraphicalEffects

import "../../cores" as Cores
import "../Base"

Item {
  id: root
  height: parent.height
  width: height

  property bool selected: false
  property color selectColor: Material.color(Material.accent)
  property string tipText: ""
  property alias source: iconImage.source

  ToolTip.visible: tipText !== "" && hovered
  ToolTip.text: tipText

  Item {
    anchors.centerIn: parent
    height: parent.height * 0.9
    width: height

    Image {
      id: iconImage
      anchors.fill: parent
      fillMode: Image.PreserveAspectFit
      visible: false
    }

    ColorOverlay {
      anchors.centerIn: parent
      width: iconImage.width
      height: iconImage.height
      source: iconImage
      color: root.selected ? root.selectColor
                           : (Cores.CoreStyle.isDark ? "#eee" : "#2e2e2e")
      layer.enabled: true
      layer.effect: DropShadowBase { }
    }
  }
}

