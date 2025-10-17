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

  ColumnLayout {
    id: contentColumn
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.margins: padding
    spacing: 8

    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("\u5200\u5177\u578B\u53F7")
      valueText: root.formatWithUnit(root.toolModel, "")
      valueColor: Cores.CoreStyle.text
      valueFont.pointSize: 14
    }

    RowLayout {
      Layout.fillWidth: true
      spacing: 12

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("\u76F4\u5F84")
        valueText: root.formatWithUnit(root.toolDiameter, "mm")
        valueColor: Cores.CoreStyle.accent
        valueFont.pointSize: 14
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("\u4F7F\u7528\u65F6\u957F")
        valueText: root.formatWithUnit(root.toolUsage, "h")
        valueColor: Cores.CoreStyle.info
        valueFont.pointSize: 14
      }
    }

    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("\u9884\u671F\u5BFF\u547D")
      valueText: root.formatWithUnit(root.toolLifetime, "h")
      valueColor: Cores.CoreStyle.warning
      valueFont.pointSize: 14
    }
  }
}
