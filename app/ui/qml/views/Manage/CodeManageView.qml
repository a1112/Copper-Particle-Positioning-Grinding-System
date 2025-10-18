import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base"
import "../DriveInfo" as DriveInfo
import "../Code" as Code
import "../../cores" as Cores
import "../../datas" as Datas
import "../../Api" as Api
import "../../components/btns" as Btns

ColumnLayout {
  id: root
  spacing: 12

  readonly property var cutting: Datas.CuttingDatas
  readonly property var device: Datas.DeviceInfoData
  readonly property var status: Datas.StatusDatas

  function formatNumber(value, unit, decimals) {
    if (value === undefined || value === null || value === "" || isNaN(Number(value)))
      return "-"
    var precision = (decimals !== undefined) ? decimals : 2
    var num = Number(value)
    var text = precision >= 0 ? num.toFixed(precision) : String(num)
    return unit && unit.length > 0 ? text + " " + unit : text
  }

  function formatTime(seconds) {
    var sec = Number(seconds)
    if (isNaN(sec) || sec < 0)
      return "-"
    var h = Math.floor(sec / 3600)
    var m = Math.floor((sec % 3600) / 60)
    var s = Math.floor(sec % 60)
    var parts = []
    if (h > 0) parts.push(h + qsTr("小时"))
    if (m > 0) parts.push(m + qsTr("分钟"))
    parts.push(s + qsTr("秒"))
    return parts.join(" ")
  }

  function formatCoord(coord) {
    if (!coord)
      return "-"
    if (coord.x !== undefined || coord.y !== undefined || coord.z !== undefined) {
      var values = []
      if (coord.x !== undefined) values.push("X:" + Number(coord.x).toFixed(3))
      if (coord.y !== undefined) values.push("Y:" + Number(coord.y).toFixed(3))
      if (coord.z !== undefined) values.push("Z:" + Number(coord.z).toFixed(3))
      return values.join("  ")
    }
    if (coord instanceof Array)
      return coord.join(", ")
    return String(coord)
  }

  BaseCard {
    Layout.fillWidth: true
    ColumnLayout {
      anchors.fill: parent
      anchors.margins: 12
      spacing: 10

      Label { text: qsTr("切削统计（当前板）"); color: Cores.CoreStyle.text; font.bold: true }

      GridLayout {
        columns: 2
        columnSpacing: 18
        rowSpacing: 10
        Layout.fillWidth: true

        DriveInfo.InfoRowItem { Layout.fillWidth: true; titleText: qsTr("粒子总量"); valueText: device.particleTotal }
        DriveInfo.InfoRowItem { Layout.fillWidth: true; titleText: qsTr("切削量"); valueText: formatNumber(cutting.removalCurrent, "mm³", 1) }
        DriveInfo.InfoRowItem { Layout.fillWidth: true; titleText: qsTr("剩余"); valueText: formatNumber(cutting.removalRemaining, "mm³", 1) }
        DriveInfo.InfoRowItem { Layout.fillWidth: true; titleText: qsTr("平面高度"); valueText: formatNumber(device.planeHeight, "mm", 2) }
        DriveInfo.InfoRowItem { Layout.fillWidth: true; titleText: qsTr("总耗时"); valueText: formatTime(cutting.elapsedSec) }
        DriveInfo.InfoRowItem {
          Layout.fillWidth: true
          titleText: qsTr("预计剩余")
          valueText: formatTime(cutting.last && cutting.last.remaining_sec)
        }
        DriveInfo.InfoRowItem { Layout.fillWidth: true; titleText: qsTr("最大扭矩"); valueText: formatNumber(cutting.torqueMax, "N·m", 2) }
        DriveInfo.InfoRowItem { Layout.fillWidth: true; titleText: qsTr("最大转速"); valueText: formatNumber(status.maxSpindleRpm, "rpm", 0) }
      }
    }
  }

  BaseCard {
    Layout.fillWidth: true
    ColumnLayout {
      anchors.fill: parent
      anchors.margins: 12
      spacing: 10

      Label { text: qsTr("单次切削统计"); color: Cores.CoreStyle.text; font.bold: true }

      GridLayout {
        columns: 2
        columnSpacing: 18
        rowSpacing: 10
        Layout.fillWidth: true

        DriveInfo.InfoRowItem {
          Layout.fillWidth: true
          titleText: qsTr("切削深度")
          valueText: formatNumber(cutting.last.cut_depth || cutting.last.depth, "mm", 3)
        }
        DriveInfo.InfoRowItem {
          Layout.fillWidth: true
          titleText: qsTr("起始坐标")
          valueText: formatCoord(cutting.last.start || cutting.last.start_position)
        }
        DriveInfo.InfoRowItem {
          Layout.fillWidth: true
          titleText: qsTr("终点坐标")
          valueText: formatCoord(cutting.last.end || cutting.last.end_position)
        }
        DriveInfo.InfoRowItem {
          Layout.fillWidth: true
          Layout.columnSpan: 2
          titleText: qsTr("指令信息")
          valueText: cutting.last.command || cutting.last.gcode || "-"
          valueWrapMode: Text.WordWrap
        }
      }
    }
  }

  Code.CodeView {
    Layout.fillWidth: true
    Layout.fillHeight: true
  }

  BaseCard {
    Layout.fillWidth: true
    RowLayout {
      anchors.fill: parent
      anchors.margins: 12
      spacing: 12

      Btns.ActionButton {
        text: qsTr("开始执行")
        onClicked: Api.ApiClient.startRun(function(){}, function(status, message){ console.warn("start run failed", status, message) })
      }
      Btns.ActionButton {
        text: qsTr("停止执行")
        danger: true
        onClicked: Api.ApiClient.stopRun(function(){}, function(status, message){ console.warn("stop run failed", status, message) })
      }
      Item { Layout.fillWidth: true }
      Rectangle {
        width: 10
        height: 10
        radius: 5
        color: Datas.CodeDatas.connected ? Cores.CoreStyle.success : Cores.CoreStyle.danger
      }
      Label {
        text: Datas.CodeDatas.connected ? qsTr("指令通道已连接") : qsTr("指令通道未连接")
        color: Datas.CodeDatas.connected ? Cores.CoreStyle.success : Cores.CoreStyle.danger
      }
    }
  }
}
