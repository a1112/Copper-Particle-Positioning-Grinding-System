pragma Singleton
import QtQuick
import QtWebSockets
import "../Api" as Api
import "../datas" as Datas

QtObject {
  id: root

  property QtObject __ws: WebSocket {
    id: ws
    url: Api.Urls.base().replace("http://", "ws://") + "/ws/cutting"
    active: false

    onStatusChanged: function(status) {
      Datas.CuttingDatas.connected = (status === WebSocket.Open)
      if (status === WebSocket.Error || status === WebSocket.Closed) {
        ws.active = false
        reconnectTimer.restart()
      }
    }

    onTextMessageReceived: function(message) {
      try {
        Datas.CuttingDatas.update(JSON.parse(message))
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
