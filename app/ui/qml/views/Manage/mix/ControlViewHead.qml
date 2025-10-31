import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../enums" as Enu
import "../../../cores" as Cores
import "../../../components/Base" as BaseComponents
import "../../../components/Card"
CardBase {
  id:root
  height: Cores.CoreStyle.cardHeadHeight
  Layout.fillWidth: true
  property int viewMode: 0
  RowLayout {
    anchors.fill:parent
    spacing: 8
    BaseComponents.CardTitleLabel {
      text: qsTr("控制")
    }
    Item{
      height: 1
      Layout.fillWidth: true
    }
    RowLayout {
      spacing: 6
      Repeater {
        model: Enu.AppEnums.controlsModels
        delegate: BaseComponents.ItemDelegateBase {
          readonly property bool selected: root.viewMode == index
          text: modelData
          onClicked: root.viewMode = index
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

