import QtQuick
import QtQuick.Controls

import "../Base"
import "../Labels"
import "../../cores" as Cores

BtnBase {
  ColorImageButton {
    id: icon
    source: Cores.CoreStyle.getIconSource("arrow-pre.png")
  }

  EffectLabel {
    text: qsTr("涓婁竴鍗?)
  }
}
