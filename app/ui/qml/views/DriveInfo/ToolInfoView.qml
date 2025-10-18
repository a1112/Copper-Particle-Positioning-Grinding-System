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

  readonly property string toolModel: Datas.DeviceInfoData.toolModel || "-"
  readonly property string toolDiameter: Datas.DeviceInfoData.toolDiameter || "-"
  readonly property string toolUsage: Datas.DeviceInfoData.toolUsage || "-"
  readonly property string toolLifetime: Datas.DeviceInfoData.toolLifetime || "-"

  function formatWithUnit(value, unit) {
    if (!value || value === "-")
      return "-"
    if (!unit || unit.length === 0)
      return value
    return `${value} ${unit}`
  }

  GridLayout {
    id: contentColumn
    anchors.margins: padding
    anchors.left: parent.left
    anchors.right: parent.right
    columns: 2
    columnSpacing: 16
    rowSpacing: 10

    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("刀具型号")
      valueText: root.formatWithUnit(root.toolModel, "")
      valueColor: Cores.CoreStyle.text
      valueFont.pointSize: 14
    }

    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("直径")
      valueText: root.formatWithUnit(root.toolDiameter, "mm")
      valueColor: Cores.CoreStyle.accent
      valueFont.pointSize: 14
    }

    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("使用时长")
      valueText: root.formatWithUnit(root.toolUsage, "h")
      valueColor: Cores.CoreStyle.info
      valueFont.pointSize: 14
    }

    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("预期寿命")
      valueText: root.formatWithUnit(root.toolLifetime, "h")
      valueColor: Cores.CoreStyle.warning
      valueFont.pointSize: 14
    }
  }
}
