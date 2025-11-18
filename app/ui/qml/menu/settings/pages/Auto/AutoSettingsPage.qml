import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../../components/Base"
// 自动的参数修复
Item {
  id: root
  property string categoryId: ""
  property var data: ({})
  property var values: ({})

  onDataChanged: {
    values = cloneMap(data && data.values ? data.values : {})
    groupRepeater.model = (data && data.groups) ? data.groups : []
  }

  ColumnLayout {
    anchors.fill: parent
    spacing: 12

    Repeater {
      id: groupRepeater
      delegate: GroupBox {
        id: groupBox
        Layout.fillWidth: true
        title: (modelData && modelData.label) || (modelData && modelData.id) || qsTr("未命名分组")
        property string groupId: modelData && modelData.id ? modelData.id : ""
        GridLayout {
          id: grid
          columns: 2
          rowSpacing: 8
          columnSpacing: 12
          Repeater {
            model: modelData && modelData.fields ? modelData.fields : []
            delegate: Item {
              Layout.fillWidth: true
              Layout.columnSpan: 2
              implicitHeight: 40
              GridLayout {
                columns: 2
                columnSpacing: 12
                anchors.fill: parent
                Label {
                  text: (modelData && modelData.label) || (modelData && modelData.id) || ""
                  color: "#e5e7eb"
                  Layout.alignment: Qt.AlignVCenter
                }
                TextFieldBase {
                  id: input
                  Layout.fillWidth: true
                  text: String(root._currentValue({ groupId: groupBox.groupId, id: modelData.id, default: modelData.default }))
                  placeholderText: String(modelData && modelData.default !== undefined ? modelData.default : "")
                  onEditingFinished: root._updateValue(groupBox.groupId, modelData.id, text)
                }
              }
              property string groupId: groupBox.groupId
            }
          }
        }
      }
    }
  }

  function _currentValue(field) {
    var g = (field && field.groupId) || (field && field.group_id) || ""
    var f = field ? field.id : ""
    var groupValues = (values && values[g]) ? values[g] : {}
    var val = groupValues[f]
    if (val === undefined || val === null)
      return (field && field.default !== undefined) ? field.default : ""
    return val
  }

  function _updateValue(groupId, fieldId, raw) {
    if (!groupId || !fieldId)
      return
    var parsed = _coerceNumber(raw)
    if (!values)
      values = {}
    if (!values[groupId])
      values[groupId] = {}
    values[groupId][fieldId] = parsed
  }

  function _coerceNumber(value) {
    var num = Number(value)
    if (!Number.isNaN(num))
      return num
    return value
  }

  function cloneMap(value) {
    if (!value || typeof value !== "object" || Array.isArray(value))
      return {}
    try {
      return JSON.parse(JSON.stringify(value))
    } catch (err) {
      return {}
    }
  }

  function collectPayload() {
    return cloneMap(values)
  }
}
