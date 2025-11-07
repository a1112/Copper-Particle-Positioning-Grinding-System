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

  readonly property bool directControlEnabled: Cores.CoreControl.allowDirectControl
  enabled: directControlEnabled

  readonly property var cylinders: [
    { index: 0, label: "1" },
    { index: 1, label: "2" },
    { index: 2, label: "3" },
    { index: 3, label: "4" },
    { index: 4, label: "5" },
    { index: 5, label: "6" },
    { index: 6, label: "7" },
    { index: 7, label: "8" },
    { index: 8, label: "9" },
    { index: 9, label: "10" },
    { index: 10, label: "11" },
    { index: 11, label: "12" },
    { index: 12, label: "13" },
    { index: 13, label: "14" },
    { index: 14, label: "15" },
    { index: 15, label: "16" }
  ]

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 8
    spacing: 8

    GridLayout {
      id: grid
      columns: 4
      rowSpacing: 6
      columnSpacing: 6
      Layout.fillWidth: true

      Repeater {
        model: cylinders
        delegate: Rectangle {
          property int idx: modelData.index
          property bool open: Cores.CoreControl.isCylinderOpen(idx)
          Layout.preferredWidth: 48
          Layout.preferredHeight: 48
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
            enabled: root.directControlEnabled
            onClicked: Cores.CoreControl.toggleCylinder(idx)
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
          }
        }
      }
    }

    RowLayout {
      Layout.fillWidth: true
      spacing: 12
      Btns.ActionButton {
        Layout.fillWidth: true
        text: qsTr("全部开启")
        enabled: root.directControlEnabled
        onClicked: Cores.CoreControl.openAllCylinders()
      }
      Btns.ActionButton {
        Layout.fillWidth: true
        text: qsTr("全部关闭")
        danger: true
        enabled: root.directControlEnabled
        onClicked: Cores.CoreControl.closeAllCylinders()
      }
    }
  }

  Item {
    anchors.fill: parent
    visible: !root.directControlEnabled
    Rectangle {
      anchors.fill: parent
      radius: 8
      color: "#0f172a"
      opacity: 0.85
    }
    Label {
      anchors.centerIn: parent
      text: qsTr("常规设置已禁用设备控制")
      color: "#94a3b8"
    }
  }
}
