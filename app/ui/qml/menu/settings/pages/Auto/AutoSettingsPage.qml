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
  property var savedValues: ({})
  property var groupRepeaterModel
  property color dirtyColor: "#facc15"
  onDataChanged: {
    values = cloneMap(data && data.values ? data.values : {})
    savedValues = cloneMap(data && data.values ? data.values : {})
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

  function _savedValue(groupId, fieldId, defaultValue) {
    if (!groupId || !fieldId)
      return defaultValue
    var groupValues = (savedValues && savedValues[groupId]) ? savedValues[groupId] : {}
    var val = groupValues[fieldId]
    if (val === undefined || val === null)
      return defaultValue
    return val
  }

  function _valuesEqual(a, b) {
    if (a === b)
      return true
    var numA = Number(a)
    var numB = Number(b)
    if (!Number.isNaN(numA) && !Number.isNaN(numB))
      return numA === numB
    return String(a || "") === String(b || "")
  }

  function _isFieldDirty(groupId, fieldId, defaultValue) {
    return !_valuesEqual(_currentValue({ groupId: groupId, id: fieldId, default: defaultValue }),
                         _savedValue(groupId, fieldId, defaultValue))
  }

  function _labelColor(groupId, fieldId, defaultValue, normalColor) {
    return _isFieldDirty(groupId, fieldId, defaultValue) ? dirtyColor : normalColor
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
