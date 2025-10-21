pragma Singleton
import QtQuick
import QtWebSockets
import "../Api" as Api
import "../datas" as Datas

QtObject {
  id: root

  property QtObject __ws: WebSocket {
    id: ws
    url: Api.Urls.wsStatus()
    active: false

    onStatusChanged: function(status) {
      Datas.StatusDatas.status = status
      Datas.StatusDatas.connected = (status === WebSocket.Open)
      if (isClosedStatus(status)) {
        ws.active = false
        reconnectTimer.restart()
      }
    }

    onTextMessageReceived: function(message) {
      try {
        var payload = JSON.parse(message)
        // console.log("onTextMessageReceived ",message)
        Datas.StatusDatas.ingest(payload)
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

  function isClosedStatus(status) {
    return [WebSocket.Error, WebSocket.Closed].indexOf(status) !== -1
  }
}
