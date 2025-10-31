import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base"
import "../../cores" as Cores
import "base"
BaseCard {
  id: root
  Layout.fillWidth: true
  readonly property int padding: 12
  implicitHeight: contentColumn.implicitHeight + 6
  readonly property var command: Cores.CoreCutting.displayCommand
  readonly property bool hasCommand: command && typeof command === "object"
  readonly property int displayIndex: Cores.CoreCutting.displayIndex

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

  function currentCommand() {
    if (root.hasCommand)
      return root.command
    return Cores.CoreCutting.commandAt(root.displayIndex)
  }

  function commandInfoText() {
    var cmd = currentCommand()
    if (cmd && cmd.displayText !== undefined)
      return root.formatText(cmd.displayText)
    if (cmd && cmd.command !== undefined)
      return root.formatText(cmd.command)
    return qsTr("-")
  }

  function commandCutDepth() {
    var cmd = currentCommand()
    if (cmd && cmd.cutDepth !== undefined)
      return cmd.cutDepth
    return Cores.CoreCutting.downfeedCurrent
  }

  function commandMaxDepth() {
    var cmd = currentCommand()
    if (cmd && cmd.maxDepth !== undefined)
      return cmd.maxDepth
    return Cores.CoreCutting.downfeedTarget
  }

  function cylinderText() {
    var cmd = currentCommand()
    if (cmd && cmd.cylinderAvoid && cmd.cylinderAvoid.length)
      return cmd.cylinderAvoid.join(", ")
    return qsTr("-")
  }

  function resolveStartPoint() {
    var cmd = currentCommand()
    if (cmd && cmd.start)
      return cmd.start
    var previous = Cores.CoreCutting.previousCommand()
    if (previous && previous.end)
      return previous.end
    return null
  }

  function resolveEndPoint() {
    var cmd = currentCommand()
    if (cmd && cmd.end)
      return cmd.end
    if (cmd && cmd.robotPath && cmd.robotPath.length)
      return cmd.robotPath[cmd.robotPath.length - 1]
    return null
  }

  function commandTypeText() {
    var cmd = currentCommand()
    if (cmd && cmd.type)
      return root.formatText(cmd.type)
    return qsTr("-")
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
      valueText: root.commandTypeText()
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
      valueText: root.formatPoint(root.resolveStartPoint())
      valueColor: Cores.CoreStyle.text
      valueWrapMode: Text.WrapAnywhere
    }

    InfoRowItem {
      Layout.fillWidth: true
      titleText: qsTr("终点")
      valueText: root.formatPoint(root.resolveEndPoint())
      valueColor: Cores.CoreStyle.text
      valueWrapMode: Text.WrapAnywhere
    }
    }

    }
}
