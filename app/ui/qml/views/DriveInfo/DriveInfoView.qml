import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base"
import "../../cores" as Cores
import "../../datas" as Datas
import "../Charts" as Charts
import "base"

// 设备状态信息
BaseCard {
  id: root
  Layout.fillWidth: true
  readonly property var status: {
    var payload = Datas.StatusDatas.lastMessage
    if (payload === undefined)
      return {}
    if (payload === null)
      return {}
    return payload
  }

  function formatNumber(value, unit, decimals) {
    if (value === undefined)
      return "-"
    if (value === null)
      return "-"
    if (value === "")
      return "-"
    if (isNaN(Number(value)))
      return "-"
    var precision = (decimals !== undefined) ? decimals : 2
    var num = Number(value)
    var text = precision >= 0 ? num.toFixed(precision) : String(num)
    return unit && unit.length > 0 ? text + " " + unit : text
  }

  function formatText(value) {
    if (value === undefined)
      return "-"
    if (value === null)
      return "-"
    var text = String(value)
    return text.length === 0 ? "-" : text
  }

  function resolvePosition(axis) {
    var position = status.position
    if (position === undefined)
      return undefined
    if (position === null)
      return undefined
    return position[axis]
  }

  function pickValue(primary, fallback) {
    if (primary !== undefined && primary !== null && primary !== "")
      return primary
    return fallback
  }

  height: columnLayout.implicitHeight

  ColumnLayout {
    id: columnLayout

    spacing: 12
    Layout.fillWidth: true

    RowLayout {
      Layout.fillWidth: true
      spacing: 10

      Label {
        text: qsTr("连接状态")
        color: Cores.CoreStyle.muted
        Layout.preferredWidth: 64
      }

      Rectangle {
        width: 10
        height: 10
        radius: 5
        color: Datas.StatusDatas.connected ? Cores.CoreStyle.success : Cores.CoreStyle.danger
      }

      Label {
        text: Datas.StatusDatas.connected ? qsTr("已连接") : qsTr("未连接")
        color: Datas.StatusDatas.connected ? Cores.CoreStyle.success : Cores.CoreStyle.danger
      }

      Item { Layout.fillWidth: true }

      Label {
        text: qsTr("状态: %1").arg(formatText(status.state))
        color: Cores.CoreStyle.text
      }
    }

    ColumnLayout {
      Layout.fillWidth: true
      RowLayout{
        Layout.fillWidth: true
      InfoRowItem { Layout.fillWidth: true; titleText: qsTr("X"); valueText: formatNumber(resolvePosition("x"), "mm", 2) }
      InfoRowItem { Layout.fillWidth: true; titleText: qsTr("Y "); valueText: formatNumber(resolvePosition("y"), "mm", 2) }
      InfoRowItem { Layout.fillWidth: true; titleText: qsTr("Z "); valueText: formatNumber(resolvePosition("z"), "mm", 2) }
        }

      Row{
      InfoRowItem { Layout.fillWidth: true; titleText: qsTr("主轴转速"); valueText: formatNumber(status.spindle_rpm, "rpm", 0); valueColor: Cores.CoreStyle.accent }
      InfoRowItem { Layout.fillWidth: true; titleText: qsTr("扭矩"); valueText: formatNumber(status.spindle_torque, "N·m", 2); valueColor: Cores.CoreStyle.info }
      InfoRowItem { Layout.fillWidth: true; titleText: qsTr("切削速度"); valueText: formatNumber(pickValue(status.feed_rate, status.cutting_speed), "mm/s", 2) }
      InfoRowItem { Layout.fillWidth: true; Layout.columnSpan: 3; titleText: qsTr("移动速度"); valueText: formatNumber(pickValue(status.travel_speed, status.motion_speed), "mm/s", 2) }
    }

    RowLayout {
      Layout.fillWidth: true
      Layout.preferredHeight: 180
      spacing: 12

      Charts.RpmChart {
        id: rpmChart
        Layout.fillWidth: true
        Layout.preferredHeight: 180
        series: Datas.StatusDatas.seriesA
      }

      Charts.TorqueChart {
        id: torqueChart
        Layout.fillWidth: true
        Layout.preferredHeight: 180
        series: Datas.StatusDatas.seriesB
      }
    }
  }

  Connections {
    target: Datas.StatusDatas
    function onMessageReceived(_) {
      rpmChart.repaint()
      torqueChart.repaint()
    }
  }
}
