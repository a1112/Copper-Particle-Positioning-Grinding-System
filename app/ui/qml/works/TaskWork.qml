pragma Singleton
import QtQuick
import "../Api" as Api
import "../datas" as Datas

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

  function refresh() {
    Api.ApiClient.get("/data/tasks/state", function(payload) {
      try {
        Datas.TaskDatas.applyState(payload)
        if (payload && payload.workpiece)
          Datas.DeviceInfoData.applyWorkpiece(payload.workpiece)
        if (payload && payload.gcode) {
          var gcode = payload.gcode
          var commands = []
          if (Array.isArray(gcode)) {
            commands = gcode
          } else if (gcode && Array.isArray(gcode.commands)) {
            commands = gcode.commands
          }
          if (commands.length)
            Datas.CodeDatas.lines = commands
          else if (payload && payload.gcode !== undefined)
            Datas.CodeDatas.lines = []
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
