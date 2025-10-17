pragma Singleton
import QtQuick
import QtWebSockets
import "../Api" as Api
import "../datas" as Datas

QtObject {
  id: root

  property QtObject __ws: WebSocket {
    id: ws
    url: Api.Urls.wsCode()
    active: false

    onStatusChanged: function(status) {
      Datas.CodeDatas.connected = (status === WebSocket.Open)
      if (status === WebSocket.Error || status === WebSocket.Closed) {
        ws.active = false
        reconnectTimer.restart()
      }
    }

    onTextMessageReceived: function(message) {
      try {
        var payload = JSON.parse(message)
        if (payload.type === "program" && Array.isArray(payload.lines)) {
          Datas.CodeDatas.lines = payload.lines
        } else if (payload.type === "state") {
          Datas.CodeDatas.runState = payload.state || "IDLE"
          Datas.CodeDatas.currentIndex = (payload.current !== undefined ? payload.current : -1)
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
}
