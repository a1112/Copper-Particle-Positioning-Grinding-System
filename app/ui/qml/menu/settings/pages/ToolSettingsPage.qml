import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
  id: page
  property var tools: []
  property ListModel toolModel: ListModel { }

  onToolsChanged: reload()
  Component.onCompleted: reload()

  function reload() {
    toolModel.clear()
    if (!Array.isArray(tools))
      return
    for (var i = 0; i < tools.length; ++i) {
      var item = tools[i] || {}
      toolModel.append({
        id: item.id || 0,
        model: item.model || "",
        diameter: item.diameter_mm || 0,
        length: item.length_mm || 0,
        usage: item.usage_minutes || 0,
        life: item.service_life_minutes || 0,
        status: item.status || 0
      })
    }
  }

  function collectPayload() {
    var result = []
    for (var i = 0; i < toolModel.count; ++i) {
      var entry = toolModel.get(i)
      result.push({
        id: entry.id,
        model: entry.model,
        diameter_mm: Number(entry.diameter) || 0,
        length_mm: Number(entry.length) || 0,
        usage_minutes: parseInt(entry.usage, 10) || 0,
        service_life_minutes: parseInt(entry.life, 10) || 0,
        status: parseInt(entry.status, 10) || 0
      })
    }
    return { tools: result }
  }

  function importFromArray(arr) {
    tools = arr
    reload()
  }

  function addTool() {
    toolModel.append({ id: 0, model: "", diameter: 0, length: 0, usage: 0, life: 0, status: 0 })
  }

  function removeTool(index) {
    if (index >= 0 && index < toolModel.count)
      toolModel.remove(index)
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 16
    spacing: 12

    RowLayout {
      Layout.fillWidth: true
      Label {
        text: qsTr("刀具参数设置")
        font.pixelSize: 18
        font.bold: true
        color: "#f8fafc"
      }
      Item { Layout.fillWidth: true }
      Button {
        text: qsTr("新增刀具")
        onClicked: addTool()
      }
    }

    Rectangle {
      Layout.fillWidth: true
      Layout.fillHeight: true
      radius: 6
      color: "#111827"
      border.color: "#1f2937"

      ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 6

        RowLayout {
          Layout.fillWidth: true
          spacing: 12
          Label { text: qsTr("型号"); color: "#93c5fd"; Layout.preferredWidth: 140 }
          Label { text: qsTr("直径(mm)"); color: "#93c5fd"; Layout.preferredWidth: 90 }
          Label { text: qsTr("长度(mm)"); color: "#93c5fd"; Layout.preferredWidth: 90 }
          Label { text: qsTr("使用时长(min)"); color: "#93c5fd"; Layout.preferredWidth: 120 }
          Label { text: qsTr("设计寿命(min)"); color: "#93c5fd"; Layout.preferredWidth: 130 }
          Label { text: qsTr("状态"); color: "#93c5fd"; Layout.preferredWidth: 70 }
          Item { Layout.fillWidth: true }
        }

        ListView {
          id: toolList
          Layout.fillWidth: true
          Layout.fillHeight: true
          model: toolModel
          clip: true
          spacing: 4
          delegate: Rectangle {
            width: toolList.width
            height: 48
            color: index % 2 === 0 ? "#16213a" : "#111827"
            border.color: "#1f2937"
            radius: 4

            RowLayout {
              anchors.fill: parent
              anchors.margins: 6
              spacing: 12

              TextField {
                text: model
                Layout.preferredWidth: 140
                placeholderText: qsTr("型号")
                onTextChanged: toolModel.setProperty(index, "model", text)
              }

              TextField {
                text: String(diameter)
                Layout.preferredWidth: 90
                inputMethodHints: Qt.ImhPreferNumbers
                onEditingFinished: toolModel.setProperty(index, "diameter", Number(text) || 0)
              }

              TextField {
                text: String(length)
                Layout.preferredWidth: 90
                inputMethodHints: Qt.ImhPreferNumbers
                onEditingFinished: toolModel.setProperty(index, "length", Number(text) || 0)
              }

              TextField {
                text: String(usage)
                Layout.preferredWidth: 120
                inputMethodHints: Qt.ImhDigitsOnly
                onEditingFinished: toolModel.setProperty(index, "usage", parseInt(text, 10) || 0)
              }

              TextField {
                text: String(life)
                Layout.preferredWidth: 130
                inputMethodHints: Qt.ImhDigitsOnly
                onEditingFinished: toolModel.setProperty(index, "life", parseInt(text, 10) || 0)
              }

              TextField {
                text: String(status)
                Layout.preferredWidth: 70
                inputMethodHints: Qt.ImhDigitsOnly
                onEditingFinished: toolModel.setProperty(index, "status", parseInt(text, 10) || 0)
              }

              ToolButton {
                text: "✕"
                onClicked: removeTool(index)
              }
            }
          }
        }
      }
    }
  }
}
