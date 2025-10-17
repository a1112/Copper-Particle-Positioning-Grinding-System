import QtQuick
import QtQuick.Controls.Material
import "../../cores" as Cores

Menu {
  id: control
  padding: 6
  leftPadding: 8
  rightPadding: 8
  topPadding: 6
  bottomPadding: 6
  background: Rectangle {
    implicitWidth: control.contentItem ? control.contentItem.implicitWidth + control.leftPadding + control.rightPadding : 120
    implicitHeight: control.contentItem ? control.contentItem.implicitHeight + control.topPadding + control.bottomPadding : 40
    radius: 8
    color: Qt.lighter(Cores.CoreStyle.surface, 1.12)
    border.width: 1
    border.color: Qt.darker(Cores.CoreStyle.border, 1.1)
  }
}

