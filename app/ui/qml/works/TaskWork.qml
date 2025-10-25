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
}
