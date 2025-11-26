pragma Singleton
import QtQuick
import "../datas" as Datas

QtObject {
  id: buttonState

  function _normalize(value, fallback) {
    if (value === undefined || value === null)
      return fallback
    var text = String(value)
    if (!text || !text.length)
      return fallback
    return text
  }

  function _mapTaskStatus(task) {
    if (!task || task.status === undefined)
      return "IDLE"
    var statusValue = Number(task.status)
    if (isNaN(statusValue))
      return "IDLE"
    switch (statusValue) {
    case 0:
      return "PENDING"
    case 1:
      return "RUNNING"
    case 2:
      return "COMPLETED"
    case 3:
      return "FAILED"
    default:
      return "IDLE"
    }
  }

  function _computeCaptureStatusReady(snapshot) {
    snapshot = snapshot || {}
    var candidates = []
    if (snapshot.state !== undefined)
      candidates.push(snapshot.state)
    if (snapshot.runState !== undefined)
      candidates.push(snapshot.runState)
    if (snapshot.run_state !== undefined)
      candidates.push(snapshot.run_state)
    for (var i = 0; i < candidates.length; ++i) {
      var text = String(candidates[i] || "").trim()
      if (!text.length)
        continue
      var upper = text.toUpperCase()
      if (upper.indexOf("READY") !== -1)
        return true
      if (upper === "IDLE")
        return true
      if (upper === "RUNNING")
        return false
      if (text.indexOf("准备就绪") !== -1)
        return true
      if (text.indexOf("重新识别") !== -1)
        return true
    }
    return true
  }

  function _actionRunningOrPaused() {
    var state = String(actionRunState || "").toUpperCase()
    return state === "RUNNING" || state === "PAUSED"
  }

  property string captureRunState: _mapTaskStatus(Datas.TaskDatas.captureTask)
  property string deviceRunState: _normalize(Datas.DeviceInfoData.runState, "-")
  property string actionRunState: _normalize(Datas.CodeDatas.runState, "IDLE")

  property bool captureReadyByStatus: _computeCaptureStatusReady(Datas.StatusDatas.lastMessage)

  property bool captureAvailable: Datas.StatusDatas.controlEnabled
                                  && Datas.TaskDatas.captureReady
                                  && !Datas.TaskDatas.alarmLocked
                                  && captureReadyByStatus
                                  && captureRunState !== "RUNNING"

  property bool deviceAvailable: Datas.StatusDatas.controlEnabled
                                 && Datas.TaskDatas.executeReady
                                 && !Datas.TaskDatas.alarmLocked

  property bool actionStartAvailable: Datas.StatusDatas.controlEnabled
                                      && actionRunState !== "RUNNING"
  property bool actionStopAvailable: Datas.StatusDatas.controlEnabled && _actionRunningOrPaused()
  property bool actionResetAvailable: actionStopAvailable
  property bool actionReplayAvailable: actionStopAvailable

  property bool estopEnable: {
    var running = false
    var deviceUpper = String(deviceRunState || "").toUpperCase()
    if (deviceUpper === "RUNNING")
      running = true
    if (captureRunState === "RUNNING" || actionRunState === "RUNNING")
      running = true
    return Datas.StatusDatas.forceEnableControls || running
  }
}
