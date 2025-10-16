import QtQuick
import QtQuick.Controls

import "../Base"
import "../Labels"
import "../../cores" as Cores

BtnBase {
  EffectLabel {
    text: qsTr("\u4e0b\u4e00\u5377")
  }

  ColorImageButton {
    id: icon
    height: parent.height
    width: height
    source: Cores.CoreStyle.getIconSource("arrow-next.png")
    scale: hovered && cliac_enabled ? 1.3 : 1

    Behavior on scale {
      NumberAnimation {
        duration: 300
      }
    }
  }
}
