import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../cores" as Cores
import "../../../components/Base" as BaseComponents
Item {
      height: Cores.CoreStyle.cardHeadHeight
       Layout.fillWidth: true
    RowLayout {
      anchors.fill:parent
      spacing: 8

        Item{
            height: 1
            Layout.fillWidth: true
        }
      RowLayout {
        spacing: 6
        Repeater {
          model: [
            { label: qsTr("气缸"), value: 0 },
            { label: qsTr("主轴"), value: 1 }
          ]
          delegate: BaseComponents.ItemDelegateBase {
            required property var modelData
            readonly property bool selected: root.viewMode === modelData.value
            text: modelData.label
            onClicked: root.viewMode = modelData.value
            background: Rectangle {
              anchors.fill: parent
              radius: 10
              color: selected ? Cores.CoreStyle.accent : (parent.hovered ? Qt.lighter(Cores.CoreStyle.surface, 1.1) : "transparent")
              border.width: 1
              border.color: selected ? Cores.CoreStyle.accent : (parent.hovered ? Qt.lighter(Cores.CoreStyle.accent, 1.2) : Cores.CoreStyle.border)
              opacity: selected ? 0.3 : 1.0
            }
            contentItem: Label {
              text: parent.text
              font.bold: selected
              color: selected ? Cores.CoreStyle.text : (parent.hovered ? Cores.CoreStyle.accent : Cores.CoreStyle.muted)
              horizontalAlignment: Text.AlignHCenter
              verticalAlignment: Text.AlignVCenter
              padding: 4
            }
          }
        }
      }
    }

}

