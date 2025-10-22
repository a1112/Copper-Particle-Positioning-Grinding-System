pragma Singleton
import QtQuick
// Field mappings documented in docs/ui_data_contracts.md (status payload section)
import "../cores" as Core

QtObject {
  id: root

  property string serialNumber: "-"
  property string runMode: Core.CoreState.currentRunModelName
  property string runState: "-"

  property string particleTotal: "-"
  property string planeHeight: "-"

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
    if (payload.serialNumber !== undefined)
      serialNumber = _toDisplay(payload.serialNumber)
    else if (payload.serial_number !== undefined)
      serialNumber = _toDisplay(payload.serial_number)
    if (payload.runMode !== undefined)
      runMode = _toDisplay(payload.runMode)
    else if (payload.run_mode !== undefined)
      runMode = _toDisplay(payload.run_mode)
    if (payload.runState !== undefined)
      runState = _toDisplay(payload.runState)
    else if (payload.state !== undefined)
      runState = _toDisplay(payload.state)
    if (payload.particleTotal !== undefined)
      particleTotal = _toDisplay(payload.particleTotal)
    else if (payload.particle_count !== undefined)
      particleTotal = _toDisplay(payload.particle_count)
    if (payload.planeHeight !== undefined)
      planeHeight = _toDisplay(payload.planeHeight)
    else if (payload.plane_height !== undefined)
      planeHeight = _toDisplay(payload.plane_height)
  }

  function reset() {
    serialNumber = "-"
    runMode = Core.CoreState.currentRunModelName
    runState = "-"
    particleTotal = "-"
    planeHeight = "-"
  }
}
