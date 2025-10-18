import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import "../../../cores" as Cores

Popup {
  id: control
  modal: false
  focus: true
  padding: 10
  implicitWidth: 220
  implicitHeight: Math.max(contentItem.implicitHeight + padding * 2, 48)
  closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

  property var infoViewCore: null
  property Item anchorItem: null

  x: anchorItem ? anchorItem.mapToItem(null, anchorItem.width - width, anchorItem.height).x : 0
  y: anchorItem ? anchorItem.mapToItem(null, 0, anchorItem.height).y : 0

  background: Rectangle {
    radius: 8
    color: Qt.lighter(Cores.CoreStyle.surface, 1.05)
    border.width: 1
    border.color: Cores.CoreStyle.border
  }

  contentItem: Column {
    spacing: 6
    Repeater {
      model: control.infoViewCore ? control.infoViewCore.views : []
      delegate: CheckDelegate {
        width: control.implicitWidth - control.padding * 2
        implicitHeight: 30
        text: modelData.title
        Material.accent: Cores.CoreStyle.accent
        checked: control.infoViewCore ? control.infoViewCore.isSelected(modelData.key) : false
        onToggled: {
          if (control.infoViewCore)
            control.infoViewCore.setSelected(modelData.key, checked)
        }
      }
    }
  }
}
