pragma Singleton
import QtQuick
import "../cores" as Core

QtObject {
  id: root

  property string serialNumber: "-"
  property string runMode: Core.CoreState.currentRunModelName
  property string runState: "-"

  property string toolModel: "-"
  property string toolDiameter: "-"
  property string toolUsage: "-"
  property string toolLifetime: "-"

  property string particleTotal: "-"
  property string planeHeight: "-"

  function _toDisplay(value) {
    if (value === undefined || value === null)
      return "-"
    var text = String(value)
    text = text.trim()
    return text.length === 0 ? "-" : text
  }

  function applySnapshot(payload) {
    if (!payload)
      return
    if (payload.serialNumber !== undefined || payload.serial_number !== undefined)
      serialNumber = _toDisplay(payload.serialNumber !== undefined ? payload.serialNumber : payload.serial_number)
    if (payload.runMode !== undefined || payload.run_mode !== undefined)
      runMode = _toDisplay(payload.runMode !== undefined ? payload.runMode : payload.run_mode)
    if (payload.runState !== undefined || payload.state !== undefined)
      runState = _toDisplay(payload.runState !== undefined ? payload.runState : payload.state)

    if (payload.toolModel !== undefined || payload.tool_model !== undefined || payload.toolName !== undefined)
      toolModel = _toDisplay(payload.toolModel !== undefined ? payload.toolModel : (payload.tool_model !== undefined ? payload.tool_model : payload.toolName))
    if (payload.toolDiameter !== undefined || payload.cutter_diameter !== undefined)
      toolDiameter = _toDisplay(payload.toolDiameter !== undefined ? payload.toolDiameter : payload.cutter_diameter)
    if (payload.toolUsage !== undefined || payload.tool_usage !== undefined)
      toolUsage = _toDisplay(payload.toolUsage !== undefined ? payload.toolUsage : payload.tool_usage)
    if (payload.toolLifetime !== undefined || payload.tool_life !== undefined)
      toolLifetime = _toDisplay(payload.toolLifetime !== undefined ? payload.toolLifetime : payload.tool_life)

    if (payload.particleTotal !== undefined || payload.particle_count !== undefined)
      particleTotal = _toDisplay(payload.particleTotal !== undefined ? payload.particleTotal : payload.particle_count)
    if (payload.planeHeight !== undefined || payload.plane_height !== undefined)
      planeHeight = _toDisplay(payload.planeHeight !== undefined ? payload.planeHeight : payload.plane_height)
  }

  function reset() {
    serialNumber = "-"
    runMode = Core.CoreState.currentRunModelName
    runState = "-"
    toolModel = "-"
    toolDiameter = "-"
    toolUsage = "-"
    toolLifetime = "-"
    particleTotal = "-"
    planeHeight = "-"
  }
}
