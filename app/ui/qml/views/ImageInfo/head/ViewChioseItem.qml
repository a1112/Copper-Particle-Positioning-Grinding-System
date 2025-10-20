import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material

import "../../../cores" as Cores
import "../../../components/Base"

ItemDelegateBase {
  id: root

  property bool selected: Cores.CoreState.realViewIndex === index

  padding: 10
  implicitWidth: Math.max(contentItem.implicitWidth + padding * 2, 96)

  onClicked: Cores.CoreState.realViewIndex = index

  background: Rectangle {
    anchors.fill: parent
    radius: 10
    color: root.selected ? Cores.CoreStyle.accent :
           (root.hovered ? Qt.lighter(Cores.CoreStyle.surface, 1.1) : "transparent")
    opacity: root.selected ? 0.28 : (root.hovered ? 0.6 : 1.0)
    border.width: 1
    border.color: root.selected ? Cores.CoreStyle.accent :
                    (root.hovered ? Qt.lighter(Cores.CoreStyle.accent, 1.3) : Cores.CoreStyle.border)
    Behavior on color { ColorAnimation { duration: 140 } }
    Behavior on opacity { NumberAnimation { duration: 140 } }
    Behavior on border.color { ColorAnimation { duration: 140 } }
  }

  contentItem: Label {
    text: root.text
    font.bold: root.selected
    color: root.selected ? Cores.CoreStyle.text :
             (root.hovered ? Cores.CoreStyle.accent : Cores.CoreStyle.muted)
    horizontalAlignment: Text.AlignHCenter
    verticalAlignment: Text.AlignVCenter
    wrapMode: Text.NoWrap
  }
}
