pragma Singleton
import QtQuick

QtObject {
  id: root

  property int workpieceId: 0
  property string workpieceCode: "-"
  property string workpieceType: "-"
  property string serialNumber: "-"
  property int latestRecordId: 0
  property int readyRecordId: 0

  property var captureTask: ({})
  property var executeTask: ({})
  property var controlTask: ({})
  property var readyState: ({})

  property bool captureReady: true
  property bool executeReady: true
  property bool controlReady: true

  function reset() {
    workpieceId = 0
    workpieceCode = "-"
    workpieceType = "-"
    serialNumber = "-"
    latestRecordId = 0
    readyRecordId = 0
    captureTask = ({})
    executeTask = ({})
    controlTask = ({})
    readyState = ({})
    captureReady = true
    executeReady = true
    controlReady = true
  }

  function _clone(input) {
    if (input === undefined || input === null)
      return ({})
    if (typeof input === "object")
      return input
    return ({ value: input })
  }

  function applyState(payload) {
    if (!payload) {
      reset()
      return
    }
    var workpiece = payload.workpiece || {}
    if (workpiece.id !== undefined)
      workpieceId = workpiece.id
    if (workpiece.code !== undefined)
      workpieceCode = String(workpiece.code)
    if (workpiece.type !== undefined)
      workpieceType = String(workpiece.type)
    serialNumber = (workpieceId && workpieceId > 0) ? ("#" + workpieceId) : "-"

    latestRecordId = payload.latest_record || 0
    readyRecordId = (payload.ready && payload.ready.record_id) ? payload.ready.record_id : 0

    captureTask = _clone(payload.capture)
    executeTask = _clone(payload.execute)
    controlTask = _clone(payload.control)
    readyState = _clone(payload.ready)

    captureReady = !!(readyState.capture !== false)
    executeReady = !!readyState.execute
    controlReady = !!(readyState.control === undefined || readyState.control)
  }
}
