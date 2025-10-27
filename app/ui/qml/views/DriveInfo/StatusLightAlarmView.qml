import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base"
import "../../cores" as Cores
import "../../datas" as Datas
import "base"

// 报警状态概览
BaseCard {
  id: root
  Layout.fillWidth: true
  readonly property var status: {
    var payload = Datas.StatusDatas.lastMessage
    if (payload === undefined)
      payload = {}
    if (payload === null)
      payload = {}
    return payload
  }
  readonly property var indicatorEntries: [
    ({ key: "camera", label: qsTr("相机") }),
    ({ key: "spindle", label: qsTr("主轴") }),
    ({ key: "device", label: qsTr("设备") }),
    ({ key: "interlock", label: qsTr("互锁") }),
    ({ key: "server", label: qsTr("服务器") })
  ]

  function _isEmptyValue(value) {
    if (value === undefined)
      return true
    if (value === null)
      return true
    return value === ""
  }

  function _lightContainers() {
    var message = status
    var buckets = []
    if (message.statusLights)
      buckets.push(message.statusLights)
    if (message.lightStates)
      buckets.push(message.lightStates)
    if (message.light_status)
      buckets.push(message.light_status)
    if (message.lightState)
      buckets.push(message.lightState)
    if (message.lights)
      buckets.push(message.lights)
    if (message.extras)
      buckets.push(message.extras)
    buckets.push(message)
    return buckets
  }

  function _keyCandidates(key) {
    return [
      key,
      key + "_status",
      key + "_light",
      key + "_state",
      key + "Status",
      key + "Light",
      key + "State"
    ]
  }

  function _rawLightValue(key) {
    var containers = _lightContainers()
    for (var i = 0; i < containers.length; ++i) {
      var bucket = containers[i]
      if (!bucket)
        continue
      if (typeof bucket !== "object")
        continue
      var keys = _keyCandidates(key)
      for (var j = 0; j < keys.length; ++j) {
        var candidate = keys[j]
        if (bucket[candidate] !== undefined)
          return bucket[candidate]
      }
    }
    return undefined
  }

  function _normalizedValue(key) {
    var raw = _rawLightValue(key)
    var text = "-"
    var tone = "unknown"
    if (_isEmptyValue(raw)) {
      // leave defaults
    } else if (typeof raw === "boolean") {
      text = raw ? qsTr("正常") : qsTr("报警")
      tone = raw ? "ok" : "error"
    } else {
      var str = String(raw).trim()
      if (str.length === 0) {
        // keep defaults
      } else {
        var upper = str.toUpperCase()
        switch (upper) {
        case "ON":
        case "RUN":
        case "RUNNING":
        case "READY":
        case "OK":
        case "NORMAL":
        case "GREEN":
        case "ACTIVE":
        case "UP":
        case "TRUE":
          text = qsTr("正常")
          tone = "ok"
          break
        case "WARN":
        case "WARNING":
        case "YELLOW":
        case "ATTENTION":
          text = qsTr("预警")
          tone = "warn"
          break
        case "OFF":
        case "FAULT":
        case "ERROR":
        case "ALARM":
        case "FAIL":
        case "RED":
        case "DOWN":
        case "STOP":
        case "FALSE":
          text = qsTr("报警")
          tone = "error"
          break
        default:
          text = str
          tone = "custom"
          break
        }
      }
    }
    return {
      raw: raw,
      text: text,
      tone: tone
    }
  }

  function colorForTone(tone) {
    switch (tone) {
    case "ok":
      return Cores.CoreStyle.success
    case "warn":
      return Cores.CoreStyle.warning
    case "error":
      return Cores.CoreStyle.danger
    case "custom":
      return Cores.CoreStyle.accent
    default:
      return Cores.CoreStyle.muted
    }
  }

  implicitHeight: contentColumn.implicitHeight + 5

  GridLayout {
    id: contentColumn
    columns: 3
    columnSpacing: 5
    rowSpacing: 5
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.margins: 2

    Repeater {
      model: root.indicatorEntries

      delegate: RowLayout {
        readonly property var stateInfo: root._normalizedValue(modelData.key)

        spacing: 1

        InfoTitleLabel {
          text: modelData.label
          horizontalAlignment: Text.AlignLeft
        }

        RowLayout {
          Layout.fillWidth: true
          spacing: 2

          Rectangle {
            width: 14
            height: 14
            radius: 7
            color: root.colorForTone(stateInfo.tone)
            border.color: color
            border.width: 1
          }

          InfoValueLabel {
            text: stateInfo.text
            color: root.colorForTone(stateInfo.tone)
            horizontalAlignment: Text.AlignLeft
            Layout.fillWidth: true
          }
        }


      }
    }
  }
}
