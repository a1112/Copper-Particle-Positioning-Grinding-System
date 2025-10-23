pragma Singleton
import QtQuick
// Field mappings documented in docs/ui_data_contracts.md (tool info section)

QtObject {
  id: root

  property string toolModel: "-"
  property string toolDiameter: "-"
  property string toolLength: "-"
  property string toolUsage: "-"
  property string toolStatus: "-"
  property string toolLifetime: "-"
  property var toolList: []

  function _toDisplay(value) {
    if (value === undefined || value === null)
      return "-"
    var text = String(value).trim()
    return text.length === 0 ? "-" : text
  }

  function _minutesToHours(value) {
    if (value === undefined || value === null)
      return "-"
    var minutes = Number(value)
    if (isNaN(minutes))
      return _toDisplay(value)
    return (minutes / 60).toFixed(1)
  }

  function applySnapshot(payload) {
    if (!payload)
      return
    if (Array.isArray(payload)) {
      toolList = payload
      if (payload.length === 0) {
        reset()
        return
      }
      var first = payload[0] || {}
      if (first.model !== undefined)
        toolModel = _toDisplay(first.model)
      if (first.diameter_mm !== undefined)
        toolDiameter = _toDisplay(first.diameter_mm)
      if (first.length_mm !== undefined)
        toolLength = _toDisplay(first.length_mm)
      if (first.usage_minutes !== undefined)
        toolUsage = _minutesToHours(first.usage_minutes)
      if (first.service_life_minutes !== undefined)
        toolLifetime = _minutesToHours(first.service_life_minutes)
      if (first.status !== undefined)
        toolStatus = _toDisplay(first.status)
      return
    }

    // Legacy payload compatibility
    if (payload.toolList !== undefined && Array.isArray(payload.toolList)) {
      applySnapshot(payload.toolList)
      return
    }

    if (payload.toolModel !== undefined)
      toolModel = _toDisplay(payload.toolModel)
    else if (payload.tool_model !== undefined)
      toolModel = _toDisplay(payload.tool_model)
    else if (payload.toolName !== undefined)
      toolModel = _toDisplay(payload.toolName)

    if (payload.toolDiameter !== undefined)
      toolDiameter = _toDisplay(payload.toolDiameter)
    else if (payload.tool_diameter !== undefined)
      toolDiameter = _toDisplay(payload.tool_diameter)
    else if (payload.cutter_diameter !== undefined)
      toolDiameter = _toDisplay(payload.cutter_diameter)

    if (payload.toolUsage !== undefined)
      toolUsage = _toDisplay(payload.toolUsage)
    else if (payload.tool_usage !== undefined)
      toolUsage = _toDisplay(payload.tool_usage)

    if (payload.toolLifetime !== undefined)
      toolLifetime = _toDisplay(payload.toolLifetime)
    else if (payload.tool_life !== undefined)
      toolLifetime = _toDisplay(payload.tool_life)
  }

  function reset() {
    toolModel = "-"
    toolDiameter = "-"
    toolLength = "-"
    toolUsage = "-"
    toolLifetime = "-"
    toolStatus = "-"
    toolList = []
  }
}

