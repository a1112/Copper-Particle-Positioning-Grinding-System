pragma Singleton
import QtQuick
import QtWebSockets
import "../Api" as Api

// Status WebSocket singleton: exposes connection state and last payload
Item {
  id: root
  readonly property int status: ws.status
  readonly property bool connected: (ws.status===WebSocket.Open)
  property int lastMsgTs: Date.now()
  property var lastMessage: ({})
  property var seriesA: []
  property var seriesB: []
  signal messageReceived(var payload)

  function reconnect(){ ws.active = false; reconnectTimer.restart() }
  function close(){ ws.active = false }
  function clearSeries(){ seriesA = []; seriesB = [] }

  WebSocket {
    id: ws
    url: Api.Urls.ws()
    active: true
    onStatusChanged: function(status){
      if (status === WebSocket.Error) { ws.active = false; reconnectTimer.restart() }
      else if (status === WebSocket.Closed) { ws.active = false; reconnectTimer.restart() }
    }
    onTextMessageReceived: function(message){
      try {
        var payload = JSON.parse(message)
        root.lastMsgTs = Date.now()
        root.lastMessage = payload
        root.messageReceived(payload)
        if (payload && payload.seriesA !== undefined) {
          root.seriesA.push(payload.seriesA); if (root.seriesA.length > 1000) root.seriesA.shift()
        }
        if (payload && payload.seriesB !== undefined) {
          root.seriesB.push(payload.seriesB); if (root.seriesB.length > 1000) root.seriesB.shift()
        }
      } catch(e) { /* ignore */ }
    }
  }

  Timer { id: reconnectTimer; interval: 2000; running: false; repeat: false; onTriggered: ws.active = true }
}
