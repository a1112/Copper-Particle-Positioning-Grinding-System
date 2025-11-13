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

  function _resolveDefectResult() {
    var gcode = Datas.TaskDatas.gcodeData || {}
    if (!gcode)
      return null
    var alg = gcode.alg_result || gcode.algResult
    if (!alg || typeof alg !== "object")
      return null
    var defect = alg.defectResult || alg.defect_result
    return (defect && typeof defect === "object") ? defect : null
  }

  function _defectValue(keys) {
    var defect = root.defectResult
    if (!defect)
      return undefined
    for (var i = 0; i < keys.length; ++i) {
      var key = keys[i]
      if (defect[key] !== undefined && defect[key] !== null)
        return defect[key]
    }
    return undefined
  }

  function _toNumber(value) {
    var num = Number(value)
    return isNaN(num) ? Number.NaN : num
  }

  readonly property var defectResult: _resolveDefectResult()
  readonly property real defectAreaTotal: _toNumber(_defectValue(["lzAreaTotalMM", "lz_area_total_mm"]))
  readonly property real defectHeightMax: _toNumber(_defectValue(["lzHeightMax", "lz_height_max"]))
  readonly property real defectParticleCount: _toNumber(_defectValue(["lzNum", "lz_num"]))

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
        valueText: Cores.CoreCutting.particleTotal
        valueColor: Cores.CoreStyle.text
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("切削量")
        valueText: root.formatNumber(Cores.CoreCutting.removalCurrent, "mm^3", 2)
        valueColor: Cores.CoreStyle.accent
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("剩余")
        valueText: root.formatNumber(Cores.CoreCutting.downfeedRemaining, "mm", 3)
        valueColor: Cores.CoreStyle.info
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("平面高度")
        valueText: Cores.CoreCutting.planeHeight
        valueColor: Cores.CoreStyle.text
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("总耗时")
        valueText: root.formatDuration(Cores.CoreCutting.elapsedSec)
        valueColor: Cores.CoreStyle.success
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("预计剩余")
        valueText: root.formatNumber(Cores.CoreCutting.removalRemaining, "mm^3", 2)
        valueColor: Cores.CoreStyle.warning
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("最大扭矩")
        valueText: root.formatNumber(Cores.CoreCutting.torqueMax, "N*m", 3)
        valueColor: Cores.CoreStyle.danger
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("最大速度")
        valueText: root.formatNumber(Cores.CoreCutting.maxFeedRate, "mm/s", 3)
        valueColor: Cores.CoreStyle.primary
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("粒子面积")
        valueText: root.formatNumber(root.defectAreaTotal, "mm^2", 2)
        valueColor: Cores.CoreStyle.warning
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("粒子最大高度")
        valueText: root.formatNumber(root.defectHeightMax, "mm", 2)
        valueColor: Cores.CoreStyle.accent
      }

      InfoRowItem {
        Layout.fillWidth: true
        titleText: qsTr("粒子数量")
        valueText: root.formatNumber(root.defectParticleCount, qsTr("个"), 0)
        valueColor: Cores.CoreStyle.info
      }
    }
  }
}

