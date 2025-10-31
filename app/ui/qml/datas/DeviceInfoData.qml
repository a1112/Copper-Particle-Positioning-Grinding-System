pragma Singleton
import QtQuick
// Field mappings documented in docs/ui_data_contracts.md (status payload section)
import "../cores" as Core

QtObject {
  id: root

  property int workpieceId: 0
  property string workpieceCode: "-"
  property string workpieceType: "-"

  property string serialNumber: "-"
  property string runMode: Core.CoreState.currentRunModelName
  property string runState: "-"

  property string particleTotal: "-"
  property string planeHeight: "-"

  function _toDisplay(value) {
    if (value === undefined)
      return qsTr("-")
    if (value === null)
      return qsTr("-")
    var text = String(value)
    text = text.trim()
    return text.length === 0 ? "-" : text
  }

  function applySnapshot(payload) {
    if (!payload)
      return
    if (payload.workpiece !== undefined)
      applyWorkpiece(payload.workpiece)
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

  function applyWorkpiece(workpiece) {
    if (!workpiece)
      return
    if (workpiece.id !== undefined) {
      workpieceId = workpiece.id
      serialNumber = _toDisplay(workpiece.id)
    }
    if (workpiece.code !== undefined)
      workpieceCode = _toDisplay(workpiece.code)
    if (workpiece.type !== undefined)
      workpieceType = _toDisplay(workpiece.type)
  }

  function reset() {
    workpieceId = 0
    workpieceCode = "-"
    workpieceType = "-"
    serialNumber = "-"
    runMode = Core.CoreState.currentRunModelName
    runState = "-"
    particleTotal = "-"
    planeHeight = "-"
  }
}

