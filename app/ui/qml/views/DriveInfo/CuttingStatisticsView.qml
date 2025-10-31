import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base"
import "../../cores" as Cores
import "../../datas" as Datas
import "base"
BaseCard {
  id: root
  Layout.fillWidth: true
  readonly property int padding: 12
  implicitHeight: contentColumn.implicitHeight+3
  height: implicitHeight
  width: parent.width
  property real maxFeedRate: 0

  function formatNumber(value, unit, decimals) {
    if (value === undefined)
      return qsTr("-")
    if (value === null)
      return qsTr("-")
    if (value === "")
      return qsTr("-")
    if (isNaN(Number(value)))
      return qsTr("-")
    var precision = (decimals !== undefined) ? decimals : 2
    var num = Number(value)
    var text = precision >= 0 ? num.toFixed(precision) : String(num)
    return unit && unit.length > 0 ? text + " " + unit : text
  }

  function formatDuration(seconds) {
    if (seconds === undefined)
      return qsTr("-")
    if (seconds === null)
      return qsTr("-")
    if (seconds === "")
      return qsTr("-")
    if (isNaN(Number(seconds)))
      return qsTr("-")
    var total = Math.max(0, Math.floor(Number(seconds)))
    var hours = Math.floor(total / 3600)
    var minutes = Math.floor((total % 3600) / 60)
    var secs = total % 60
    function pad(x) { return x < 10 ? "0" + x : String(x) }
    if (hours > 0)
      return pad(hours) + ":" + pad(minutes) + ":" + pad(secs)
    return pad(minutes) + ":" + pad(secs)
  }

  ColumnLayout {
    id: contentColumn
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.margins: padding
    spacing: 10

    GridLayout {
      columns: 2
      columnSpacing: 18
      rowSpacing: 12
      Layout.fillWidth: true

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("粒子总量")
        valueText: Datas.DeviceInfoData.particleTotal
        valueColor: Cores.CoreStyle.text
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("切削量")
        valueText: root.formatNumber(Datas.CuttingDatas.removalCurrent, "mm^3", 2)
        valueColor: Cores.CoreStyle.accent
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("剩余")
        valueText: root.formatNumber(Math.max(0, Datas.CuttingDatas.downfeedTarget - Datas.CuttingDatas.downfeedCurrent), "mm", 3)
        valueColor: Cores.CoreStyle.info
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("平面高度")
        valueText: Datas.DeviceInfoData.planeHeight
        valueColor: Cores.CoreStyle.text
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("总耗时")
        valueText: root.formatDuration(Datas.CuttingDatas.elapsedSec)
        valueColor: Cores.CoreStyle.success
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("预计剩余")
        valueText: root.formatNumber(Math.max(0, Datas.CuttingDatas.removalRemaining), "mm^3", 2)
        valueColor: Cores.CoreStyle.warning
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("最大扭矩")
        valueText: root.formatNumber(Datas.CuttingDatas.torqueMax, "N*m", 3)
        valueColor: Cores.CoreStyle.danger
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("最大速度")
        valueText: root.formatNumber(root.maxFeedRate, "mm/s", 3)
        valueColor: Cores.CoreStyle.primary
      }
    }
  }

  Connections {
    target: Datas.CuttingDatas

    function onConnectedChanged(value) {
      if (!value)
        root.maxFeedRate = 0
    }

    function onLastChanged(payload) {
      var feedSource = Datas.CuttingDatas.feedRate
      if (payload !== undefined && payload !== null && payload.feed_rate !== undefined && payload.feed_rate !== null)
        feedSource = payload.feed_rate
      var feed = Number(feedSource)
      if (!isNaN(feed) && feed > root.maxFeedRate)
        root.maxFeedRate = feed
    }
  }
}

