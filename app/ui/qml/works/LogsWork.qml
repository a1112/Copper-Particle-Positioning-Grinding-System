pragma Singleton
import QtQuick
import QtWebSockets
import "../Api" as Api
import "../datas" as Datas

QtObject {
  id: root

  property QtObject __ws: WebSocket {
    id: ws
    url: Api.Urls.wsLogs()
    active: false

    onStatusChanged: function(status) {
      Datas.LogDatas.status = status
      Datas.LogDatas.connected = (status === WebSocket.Open)
      if (status === WebSocket.Error || status === WebSocket.Closed) {
        ws.active = false
        reconnectTimer.restart()
      }
    }

    onTextMessageReceived: function(message) {
      try {
        var payload = JSON.parse(message)
        if (payload.type === "history" && Array.isArray(payload.items)) {
          Datas.LogDatas.appendMany(payload.items)
        } else if (payload.type === "append" && payload.item) {
          Datas.LogDatas.append(payload.item)
        }
      } catch (e) {
        // ignore malformed payload
      }
    }
  }

  property Timer __reconnectTimer: Timer {
    id: reconnectTimer
    interval: 2000
    running: false
    repeat: false
    onTriggered: ws.active = true
  }

  function start() {
    if (!ws.active)
      ws.active = true
  }

  function stop() {
    reconnectTimer.stop()
    ws.active = false
  }

  function reconnect() {
    stop()
    reconnectTimer.restart()
  }

  function clearLocalLogs() {
    Datas.LogDatas.clear()
  }

  function sendServerLog(msg) {
    Api.ApiClient.post("/test/log?msg=" + encodeURIComponent(msg || "UI log"), {}, function(_) {}, function(status, message) {
      console.log("send log err", status, message)
    })
  }

  function clearServerLogs() {
    Api.ApiClient.post("/test/log/clear", {}, function(_) {}, function(status, message) {
      console.log("clear logs err", status, message)
    })
  }
}
