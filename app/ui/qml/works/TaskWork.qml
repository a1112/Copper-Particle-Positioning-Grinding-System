pragma Singleton
import QtQuick
import "../Api" as Api
import "../datas" as Datas
import "../cores" as Cores

QtObject {
  id: root

  property Timer pollTimer: Timer {
    id: poller
    interval: 2500
    repeat: true
    running: false
    onTriggered: root.refresh()
  }

  function start() {
    refresh()
    if (!poller.running)
      poller.start()
  }

  function stop() {
    poller.stop()
  }

  property int _prevCaptureRecordId: 0
  property int _prevCaptureStatus: -1
  property int _prevLatestRecordId: 0

  function refresh() {
    Api.ApiClient.get("/data/tasks/state", function(payload) {
      try {
        Datas.TaskDatas.applyState(payload)
        if (payload && payload.workpiece)
          Datas.DeviceInfoData.applyWorkpiece(payload.workpiece)
        if (payload && payload.gcode !== undefined) {
          Cores.CoreCutting.loadProgram(payload.gcode)
        }
        var capture = payload && payload.capture ? payload.capture : null
        var captureRecordId = capture && capture.record_id !== undefined ? Number(capture.record_id) : 0
        var captureStatus = capture && capture.status !== undefined ? Number(capture.status) : -1
        var latestRecordId = payload && payload.latest_record !== undefined ? Number(payload.latest_record) : 0

        if (isNaN(captureRecordId))
          captureRecordId = 0
        if (isNaN(captureStatus))
          captureStatus = -1
        if (isNaN(latestRecordId))
          latestRecordId = 0

        var captureStatusChanged = (captureRecordId !== _prevCaptureRecordId) || (captureStatus !== _prevCaptureStatus)
        var recordChanged = latestRecordId !== _prevLatestRecordId && latestRecordId > 0
        _prevCaptureRecordId = captureRecordId
        _prevCaptureStatus = captureStatus
        _prevLatestRecordId = latestRecordId

        if ((captureStatusChanged && captureStatus === 2) || recordChanged) {
          if (Cores && Cores.CoreState && Cores.CoreState.refreshDataSources)
            Cores.CoreState.refreshDataSources()
        }
      } catch (err) {
        console.warn("TaskWork refresh parse failed", err)
      }
    }, function(status, message) {
      console.warn("TaskWork refresh error", status, message)
    })
  }

  function enqueueExecute(recordId, workpieceId, onOk, onErr) {
    var body = {}
    if (recordId)
      body.record_id = recordId
    if (!body.record_id && workpieceId)
      body.workpiece_id = workpieceId
    Api.ApiClient.post("/data/tasks/execute", body, function(resp) {
      refresh()
      if (onOk)
        onOk(resp)
    }, function(status, message) {
      if (onErr)
        onErr(status, message)
    })
  }

  function clearCommands(onOk, onErr) {
    Api.ApiClient.del("/data/tasks/control", function(resp) {
      refresh()
      if (onOk)
        onOk(resp)
    }, function(status, message) {
      if (onErr)
        onErr(status, message)
    })
  }

  function deleteCommand(id, onOk, onErr) {
    if (!id)
      return
    Api.ApiClient.del("/data/tasks/control/" + encodeURIComponent(id), function(resp) {
      refresh()
      if (onOk)
        onOk(resp)
    }, function(status, message) {
      if (onErr)
        onErr(status, message)
    })
  }
}

