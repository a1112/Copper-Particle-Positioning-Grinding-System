pragma Singleton
import QtQuick
// Field mappings documented in docs/ui_data_contracts.md (tool info section)

QtObject {
  id: root

  property string toolModel: "-"
  property string toolDiameter: "-"
  property string toolUsage: "-"
  property string toolLifetime: "-"

  function _toDisplay(value) {
    if (value === undefined)
      return "-"
    if (value === null)
      return "-"
    var text = String(value)
    text = text.trim()
    return text.length === 0 ? "-" : text
  }

  function applySnapshot(payload) {
    if (!payload)
      return
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
    toolUsage = "-"
    toolLifetime = "-"
  }
}
