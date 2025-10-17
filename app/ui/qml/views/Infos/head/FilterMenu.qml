import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import "../../../cores" as Cores

Menu {
  id: control
  modal: false
  focus: true
  padding: 10
  implicitWidth: 220
  implicitHeight: Math.max(contentItem.implicitHeight + padding * 2, 40)
  closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside


  property Item anchorItem: null

  background: Rectangle {
    radius: 8
    color: Qt.lighter(Cores.CoreStyle.surface, 1.05)
    border.width: 1
    border.color: Cores.CoreStyle.border
  }

   Column {
    spacing: 4
    Repeater {
      model: infoViewCore.views
      delegate: CheckDelegate {
        id: optionDelegate
        width: control.implicitWidth - control.padding * 2
        implicitHeight: 30
        text: modelData.title
        Material.accent: Cores.CoreStyle.accent
        Binding {
          target: optionDelegate
          property: "checked"
          value: infoViewCore ? infoViewCore.isSelected(modelData.key) : false
        }
        onToggled: {
            infoViewCore.setSelected(modelData.key, checked)
        }
      }
    }
  }
}
