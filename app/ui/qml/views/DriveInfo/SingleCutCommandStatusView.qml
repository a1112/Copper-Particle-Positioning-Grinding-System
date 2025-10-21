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
  implicitHeight: contentColumn.implicitHeight + 6

  function formatNumber(value, unit, decimals) {
    if (value === undefined)
      return "-"
    if (value === null)
      return "-"
    if (value === "")
      return "-"
    if (isNaN(Number(value)))
      return "-"
    var precision = (decimals !== undefined) ? decimals : 3
    var num = Number(value)
    var text = precision >= 0 ? num.toFixed(precision) : String(num)
    return unit && unit.length > 0 ? text + " " + unit : text
  }

  function formatText(value) {
    if (value === undefined)
      return "-"
    if (value === null)
      return "-"
    var text = String(value).trim()
    return text.length === 0 ? "-" : text
  }

  function _pickFirst(source, candidates) {
    if (!source)
      return undefined
    for (var i = 0; i < candidates.length; ++i) {
      var key = candidates[i]
      if (key in source && source[key] !== undefined && source[key] !== null)
        return source[key]
    }
    return undefined
  }

  function extractPoint(payload, mainKey, shortKey) {
    if (!payload)
      return null

    var direct = _pickFirst(payload, [
      mainKey,
      mainKey + "Point",
      mainKey + "_point",
      mainKey + "Position",
      mainKey + "_position",
      mainKey + "Coords",
      mainKey + "_coords",
      mainKey + "Coordinate",
      mainKey + "_coordinate"
    ])
    if (direct !== undefined) {
      return direct
    }

    function pickComponent(keys) {
      return _pickFirst(payload, keys)
    }

    var x = pickComponent([
      mainKey + "X", mainKey + "x", mainKey + "_x", mainKey + "_X",
      shortKey + "x", shortKey + "X", shortKey + "_x", shortKey + "_X"
    ])
    var y = pickComponent([
      mainKey + "Y", mainKey + "y", mainKey + "_y", mainKey + "_Y",
      shortKey + "y", shortKey + "Y", shortKey + "_y", shortKey + "_Y"
    ])
    var z = pickComponent([
      mainKey + "Z", mainKey + "z", mainKey + "_z", mainKey + "_Z",
      shortKey + "z", shortKey + "Z", shortKey + "_z", shortKey + "_Z"
    ])

    if (x === undefined && y === undefined && z === undefined)
      return null

    return { x: x, y: y, z: z }
  }

  function formatPoint(point) {
    if (point === null)
      return "-"
    if (point === undefined)
      return "-"
    if (typeof point === "string")
      return formatText(point)
    if (typeof point !== "object")
      return "-"

    function normalizeValue(obj, names) {
      for (var i = 0; i < names.length; ++i) {
        var key = names[i]
        if (key in obj && obj[key] !== undefined && obj[key] !== null) {
          return obj[key]
        }
      }
      return undefined
    }

    var xVal = normalizeValue(point, ["x", "X"])
    var yVal = normalizeValue(point, ["y", "Y"])
    var zVal = normalizeValue(point, ["z", "Z"])

    var parts = []
    if (xVal !== undefined && xVal !== null && xVal !== "")
      parts.push("X:" + root.formatNumber(xVal, "mm", 3))
    if (yVal !== undefined && yVal !== null && yVal !== "")
      parts.push("Y:" + root.formatNumber(yVal, "mm", 3))
    if (zVal !== undefined && zVal !== null && zVal !== "")
      parts.push("Z:" + root.formatNumber(zVal, "mm", 3))

    return parts.length > 0 ? parts.join("  ") : "-"
  }

  function depthStatus() {
    var current = Datas.CuttingDatas.downfeedCurrent
    var target = Datas.CuttingDatas.downfeedTarget
    var currentText = root.formatNumber(current, "mm", 3)
    var targetText = root.formatNumber(target, "mm", 3)
    if (currentText === "-" && targetText === "-")
      return "-"
    if (targetText === "-")
      return currentText
    if (currentText === targetText)
      return currentText
    return currentText + " / " + targetText
  }

  function commandInfoText() {
    var payload = Datas.CuttingDatas.last
    if (payload === undefined)
      payload = {}
    if (payload === null)
      payload = {}
    var fromPayload = root._pickFirst(payload, [
      "command",
      "command_text",
      "commandInfo",
      "command_info",
      "instruction",
      "instruction_text"
    ])
    if (fromPayload !== undefined)
      return root.formatText(fromPayload)

    var idx = Datas.CodeDatas.currentIndex
    var lines = Datas.CodeDatas.lines
    if (!Array.isArray(lines))
      lines = []
    if (idx !== undefined && idx >= 0 && idx < lines.length) {
      return root.formatText(lines[idx])
    }
    return "-"
  }

  ColumnLayout {
    id: contentColumn
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.margins: padding
    spacing: 10

    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("切削深度")
      valueText: root.depthStatus()
      valueColor: Cores.CoreStyle.accent
    }

    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("起始坐标")
      valueText: root.formatPoint(root.extractPoint(Datas.CuttingDatas.last, "start", "s"))
      valueColor: Cores.CoreStyle.text
      valueWrapMode: Text.WrapAnywhere
    }

    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("终点坐标")
      valueText: root.formatPoint(root.extractPoint(Datas.CuttingDatas.last, "end", "e"))
      valueColor: Cores.CoreStyle.text
      valueWrapMode: Text.WrapAnywhere
    }

    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("指令信息")
      valueText: root.commandInfoText()
      valueColor: Cores.CoreStyle.info
      valueWrapMode: Text.Wrap
    }
  }
}
