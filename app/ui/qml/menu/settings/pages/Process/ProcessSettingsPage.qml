import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../"

Page {
  id: page
  property var data: ({})
  property var formData: defaultTemplate()

  function defaultTemplate() {
    return {
      motion: {
        air_cut_speed: 0.0,
        air_cut_speed_max: 0.0,
        feed_speed: 0.0,
        feed_speed_max: 0.0,
        jog_speed: 0.0
      },
      spindle: {
        rpm: 0.0,
        tool_diameter: 0.0
      }
    }
  }

  function deepCopy(obj) { return JSON.parse(JSON.stringify(obj)) }

  function mergeDefaults(source) {
    var base = deepCopy(defaultTemplate())
    function merge(target, incoming) {
      if (!incoming) return
      for (var key in incoming) {
        if (!incoming.hasOwnProperty(key))
          continue
        var value = incoming[key]
        if (value !== null && typeof value === "object" && !Array.isArray(value)) {
          if (!(key in target) || typeof target[key] !== "object")
            target[key] = {}
          merge(target[key], value)
        } else {
          target[key] = value
        }
      }
    }
    merge(base, source)
    return base
  }

  function collectPayload() { return deepCopy(formData) }

  function getValue(path, fallback) {
    var node = formData
    var parts = path.split(".")
    for (var i = 0; i < parts.length; ++i) {
      var key = parts[i]
      if (!node || !(key in node))
        return fallback
      node = node[key]
    }
    return node !== undefined ? node : fallback
  }

  function setValue(path, value) {
    var parts = path.split(".")
    var node = formData
    for (var i = 0; i < parts.length - 1; ++i) {
      var key = parts[i]
      if (!(key in node) || typeof node[key] !== "object")
        node[key] = {}
      node = node[key]
    }
    node[parts[parts.length - 1]] = value
    formData = deepCopy(formData)
  }

  function setNumeric(path, textValue) {
    var value = Number(textValue)
    if (isNaN(value))
      value = 0
    setValue(path, value)
  }

  onDataChanged: formData = mergeDefaults(data)
  Component.onCompleted: formData = mergeDefaults(data)

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 8
    spacing: 8

    Label {
      text: qsTr("工艺参数设置")
      font.pixelSize: 18
      font.bold: true
      color: "#f8fafc"
    }

    GroupBox {
      title: qsTr("运动参数")
      Layout.fillWidth: true
      ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        GridLayout {
          columns: 4
          columnSpacing: 16
          rowSpacing: 8

          Label { text: qsTr("空跑速度 (mm/s)"); color: "#e2e8f0" }
          TextFieldBase {
            text: String(getValue("motion.air_cut_speed", 0))
            onEditingFinished: setNumeric("motion.air_cut_speed", text)
          }
          Label { text: qsTr("最大空跑速度 (mm/s)"); color: "#e2e8f0" }
          TextFieldBase {
            text: String(getValue("motion.air_cut_speed_max", 0))
            onEditingFinished: setNumeric("motion.air_cut_speed_max", text)
          }

          Label { text: qsTr("进给速度 (mm/s)"); color: "#e2e8f0" }
          TextFieldBase {
            text: String(getValue("motion.feed_speed", 0))
            onEditingFinished: setNumeric("motion.feed_speed", text)
          }
          Label { text: qsTr("最大进给速度 (mm/s)"); color: "#e2e8f0" }
          TextFieldBase {
            text: String(getValue("motion.feed_speed_max", 0))
            onEditingFinished: setNumeric("motion.feed_speed_max", text)
          }

          Label { text: qsTr("点动速度 (mm/s)"); color: "#e2e8f0" }
          TextFieldBase {
            text: String(getValue("motion.jog_speed", 0))
            onEditingFinished: setNumeric("motion.jog_speed", text)
          }
        }
      }
    }

    GroupBox {
      title: qsTr("主轴 / 刀具")
      Layout.fillWidth: true
      ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        GridLayout {
          columns: 4
          columnSpacing: 16
          rowSpacing: 8

          Label { text: qsTr("主轴转速 (rpm)"); color: "#e2e8f0" }
          TextFieldBase {
            text: String(getValue("spindle.rpm", 0))
            onEditingFinished: setNumeric("spindle.rpm", text)
          }

          Label { text: qsTr("刀具直径 (mm)"); color: "#e2e8f0" }
          TextFieldBase {
            text: String(getValue("spindle.tool_diameter", 0))
            onEditingFinished: setNumeric("spindle.tool_diameter", text)
          }
        }
      }
    }

    Item { Layout.fillHeight: true }
  }
}
