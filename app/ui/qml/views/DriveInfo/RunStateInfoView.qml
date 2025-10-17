import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base"
import "../../cores" as Cores
import "../../datas" as Datas

BaseCard {
  id: root
  Layout.fillWidth: true
  readonly property int padding: 12
  implicitHeight: contentColumn.implicitHeight + padding * 2

  readonly property string runState: Datas.DeviceInfoData.runState || "-"
  readonly property string runMode: Datas.DeviceInfoData.runMode || "-"
  readonly property string serialNumber: Datas.DeviceInfoData.serialNumber || "-"

  function stateColor(state) {
    switch (String(state || "").toUpperCase()) {
    case "RUNNING":
      return Cores.CoreStyle.success
    case "ERROR":
    case "FAULT":
      return Cores.CoreStyle.danger
    case "PAUSED":
      return Cores.CoreStyle.warning
    default:
      return Cores.CoreStyle.accent
    }
  }

  ColumnLayout {
    id: contentColumn
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.margins: padding
    spacing: 8

    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("\u8FD0\u884C\u72B6\u6001")
      valueText: root.runState
      valueColor: root.stateColor(root.runState)
      valueFont.pointSize: 15
    }

    RowLayout {
      Layout.fillWidth: true
      spacing: 12

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("\u6D41\u6C34\u53F7")
        valueText: root.serialNumber
        valueColor: Cores.CoreStyle.info
        valueFont.pointSize: 15
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("\u8FD0\u884C\u6A21\u5F0F")
        valueText: root.runMode
        valueColor: Cores.CoreStyle.accent
        valueFont.pointSize: 15
      }
    }
  }
}
