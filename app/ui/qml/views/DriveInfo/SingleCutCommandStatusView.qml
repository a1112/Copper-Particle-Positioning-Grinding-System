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
  readonly property var command: Cores.CoreCutting.displayCommand
  readonly property bool hasCommand: command && typeof command === "object"

  function formatNumber(value, unit, decimals) {
    if (value === undefined)
      return qsTr("-")
    if (value === null)
      return qsTr("-")
    if (value === "")
      return qsTr("-")
    if (isNaN(Number(value)))
      return qsTr("-")
    var precision = (decimals !== undefined) ? decimals : 3
    var num = Number(value)
    var text = precision >= 0 ? num.toFixed(precision) : String(num)
    return unit && unit.length > 0 ? text + " " + unit : text
  }

  function formatText(value) {
    if (value === undefined)
      return qsTr("-")
    if (value === null)
      return qsTr("-")
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
      return qsTr("-")
    if (point === undefined)
      return qsTr("-")
    if (typeof point === "string")
      return formatText(point)
    if (typeof point !== "object")
      return qsTr("-")

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

  function commandInfoText() {
    if (root.hasCommand && root.command.displayText !== undefined)
      return root.formatText(root.command.displayText)

    var idx = Datas.CodeDatas.currentIndex
    var lines = Datas.CodeDatas.lines
    if (!Array.isArray(lines))
      lines = []
    if (idx !== undefined && idx >= 0 && idx < lines.length) {
      return root.formatText(lines[idx])
    }
    return qsTr("-")
  }

  function commandCutDepth() {
    if (root.hasCommand && root.command.cutDepth !== undefined)
      return root.command.cutDepth
    var payload = Datas.CuttingDatas.last
    if (payload && payload.cutDepth !== undefined)
      return payload.cutDepth
    return Datas.CuttingDatas.downfeedCurrent
  }

  function commandMaxDepth() {
    if (root.hasCommand && root.command.maxDepth !== undefined)
      return root.command.maxDepth
    var payload = Datas.CuttingDatas.last
    if (payload && payload.maxDepth !== undefined)
      return payload.maxDepth
    return Datas.CuttingDatas.downfeedTarget
  }

  function cylinderText() {
    if (root.hasCommand && root.command.cylinderAvoid && root.command.cylinderAvoid.length) {
      return root.command.cylinderAvoid.join(", ")
    }
    return qsTr("-")
  }

  function selectPoint(sourcePoint, fallbackKey, shortKey) {
    if (sourcePoint)
      return sourcePoint
    return root.extractPoint(Datas.CuttingDatas.last, fallbackKey, shortKey)
  }

  ColumnLayout {
    id: contentColumn
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.margins: padding
    spacing: 10
    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("指令信息")
      valueText: root.commandInfoText()
      valueColor: Cores.CoreStyle.info
      valueWrapMode: Text.Wrap
    }
    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("类型")
      valueText: root.formatText(root.hasCommand ? root.command.type : "-")
      valueColor: Cores.CoreStyle.text
    }
    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("切削深度")
      valueText: root.formatNumber(root.commandCutDepth(), "mm", 3)
      valueColor: Cores.CoreStyle.accent
    }
    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("最大深度")
      valueText: root.formatNumber(root.commandMaxDepth(), "mm", 3)
      valueColor: Cores.CoreStyle.text
    }
    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("气缸避让")
      valueText: root.cylinderText()
      valueColor: Cores.CoreStyle.text
    }
    RowLayout{
            Layout.fillWidth: true

      InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("起始")
      valueText: root.formatPoint(root.selectPoint(root.hasCommand ? root.command.start : null, "start", "s"))
      valueColor: Cores.CoreStyle.text
      valueWrapMode: Text.WrapAnywhere
    }

    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("终点")
      valueText: root.formatPoint(root.selectPoint(root.hasCommand ? root.command.end : null, "end", "e"))
      valueColor: Cores.CoreStyle.text
      valueWrapMode: Text.WrapAnywhere
    }
    }

    }
}
