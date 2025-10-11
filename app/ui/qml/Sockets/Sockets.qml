pragma Singleton
import QtQuick
import "../cores" as Cores
import QtWebSockets
import "../Api" as Api

// Global Sockets singleton: status, messages, basic chart buffers
Item {
  id: root
  // Connection state
  readonly property int status: ws.status
  readonly property bool connected: (ws.status===WebSocket.Open)
  property int lastMsgTs: Date.now()

  // Charts/data buffers (append JSON frames here)
  property var lastMessage: ({});
  property var seriesA: []    // example buffer
  property var seriesB: []
  signal messageReceived(var payload)

  // Control helpers
  function reconnect(){ ws.active = false; reconnectTimer.restart() }
  function close(){ ws.active = false }
  function clearSeries(){ seriesA = []; seriesB = [] }

  WebSocket {
    id: ws
    url: Api.Urls.ws()
    active: true
    onStatusChanged: function(status) {
      if (status === WebSocket.Error) {
        Cores.CoreError.showError("WS 连接错误: " + errorString)
        ws.active = false; reconnectTimer.restart()
      } else if (status === WebSocket.Closed) {
        ws.active = false; reconnectTimer.restart()
      }
    }
    onTextMessageReceived: function(message) {
      try {
        var payload = JSON.parse(message)
        root.lastMsgTs = Date.now()
        root.lastMessage = payload
        root.messageReceived(payload)
        // example: push values to series buffers if present
        if (payload && payload.seriesA !== undefined) {
          root.seriesA.push(payload.seriesA)
          if (root.seriesA.length > 1000) root.seriesA.shift()
        }
        if (payload && payload.seriesB !== undefined) {
          root.seriesB.push(payload.seriesB)
          if (root.seriesB.length > 1000) root.seriesB.shift()
        }
      } catch(e) { console.log('WS parse error:', e) }
    }
  }

  Timer { id: reconnectTimer; interval: 2000; running: false; repeat: false; onTriggered: ws.active = true }
}



