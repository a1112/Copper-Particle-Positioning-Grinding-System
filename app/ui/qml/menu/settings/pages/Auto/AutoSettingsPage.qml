import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../../components/Base"
// 自动的参数修复
Pane {
  id: root
  property string categoryId: ""
  property var data: ({})
  property var values: ({})
  property var groupRepeaterModel
  onDataChanged: {
    values = cloneMap(data && data.values ? data.values : {})
    groupRepeaterModel = (data && data.groups) ? data.groups : []
  }
  ColumnLayout{
    Label {
      // 标题
      font.pixelSize: 18
      font.bold: true
      color: "#f8fafc"
    }
    anchors.fill: parent

  AutoSettingsPageMain{}

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
