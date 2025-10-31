import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../cores" as Cores
import "../Base"
import "../../components/btns" as Btns

BaseCard {
  id: root
  Layout.fillWidth: true
  visible: true

  readonly property var cylinders: [
    { index: 0, label: qsTr("上1") },
    { index: 1, label: qsTr("上2") },
    { index: 2, label: qsTr("上3") },
    { index: 3, label: qsTr("上4") },
    { index: 4, label: qsTr("右1") },
    { index: 5, label: qsTr("右2") },
    { index: 6, label: qsTr("右3") },
    { index: 7, label: qsTr("右4") },
    { index: 8, label: qsTr("下1") },
    { index: 9, label: qsTr("下2") },
    { index: 10, label: qsTr("下3") },
    { index: 11, label: qsTr("下4") },
    { index: 12, label: qsTr("左1") },
    { index: 13, label: qsTr("左2") },
    { index: 14, label: qsTr("左3") },
    { index: 15, label: qsTr("左4") }
  ]

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 2
    spacing: 2
    GridLayout {
      id: grid
      columns: 4
      rowSpacing: 2
      columnSpacing: 2
      Layout.fillWidth: true

      Repeater {
        model: cylinders
        delegate: Rectangle {
          property int idx: modelData.index
          property bool open: Cores.CoreControl.isCylinderOpen(idx)
          Layout.preferredWidth: 40
          Layout.preferredHeight: 40
          radius: 6
          color: open ? Cores.CoreStyle.accent : Cores.CoreStyle.surface
          border.color: open ? Cores.CoreStyle.accent : Cores.CoreStyle.border
          border.width: open ? 1.5 : 1

          Behavior on color { ColorAnimation { duration: 120 } }
          Behavior on border.color { ColorAnimation { duration: 120 } }

          Text {
            anchors.centerIn: parent
            text: modelData.label
            color: open ? "#000000" : Cores.CoreStyle.text
            font.bold: open
          }

          MouseArea {
            anchors.fill: parent
            onClicked: Cores.CoreControl.toggleCylinder(idx)
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
          }
        }
      }
    }

    RowLayout {
      Layout.fillWidth: true
      spacing: 8
      Btns.ActionButton {
        Layout.fillWidth: true
        text: qsTr("全部开启")
        onClicked: Cores.CoreControl.openAllCylinders()
      }
      Btns.ActionButton {
        Layout.fillWidth: true
        text: qsTr("全部关闭")
        danger: true
        onClicked: Cores.CoreControl.closeAllCylinders()
      }
    }
  }
}
