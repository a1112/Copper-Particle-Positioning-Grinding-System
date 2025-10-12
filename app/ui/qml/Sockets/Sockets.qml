pragma Singleton
import QtQuick
import "../cores" as Cores
import QtWebSockets
import "../Api" as Api

// Global Sockets singleton: status, messages, charts, and logs
Item {
  id: root
  // Status WS
  readonly property int status: ws.status
  readonly property bool connected: (ws.status===WebSocket.Open)
  // Logs WS
  readonly property int logsStatus: wsLogs.status
  readonly property bool logsConnected: (wsLogs.status===WebSocket.Open)

  property int lastMsgTs: Date.now()

  // Charts/data buffers (append JSON frames here)
  property var lastMessage: ({})
  property var seriesA: []
  property var seriesB: []
  signal messageReceived(var payload)

  // Logs
  property var logs: []            // array of {ts, level, name, msg}
  property int logsMax: 1000
  signal logReceived(var item)

  // Control helpers
  function reconnect(){ ws.active = false; reconnectTimer.restart() }
  function close(){ ws.active = false }
  function clearSeries(){ seriesA = []; seriesB = [] }
  function clearLogs(){ logs = [] }
  function addLocalLog(level, name, msg){ pushLog({ ts: Date.now()/1000.0, level: level||'INFO', name: name||'local', msg: msg||'' }) }
  function pushLog(item){ if (!item) return; logs.push(item); if (logs.length > logsMax) logs.shift(); logReceived(item) }

  // Status WebSocket
  WebSocket {
    id: ws
    url: Api.Urls.ws()
    active: true
    onStatusChanged: function(status) {
      if (status === WebSocket.Error) {
        Cores.CoreError.showError("WS 链接错误: " + errorString)
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

  // Logs WebSocket (history + append)
  WebSocket {
    id: wsLogs
    url: Api.Urls.wsLogs()
    active: true
    onStatusChanged: function(status){
      if (status === WebSocket.Error) {
        wsLogs.active = false; logsReconnect.restart()
      } else if (status === WebSocket.Closed) {
        wsLogs.active = false; logsReconnect.restart()
      }
    }
    onTextMessageReceived: function(message){
      try {
        var payload = JSON.parse(message)
        if (payload.type === 'history' && Array.isArray(payload.items)){
          for (var i=0;i<payload.items.length;i++) pushLog(payload.items[i])
        } else if (payload.type === 'append' && payload.item){
          pushLog(payload.item)
        }
      } catch(e) { /* ignore */ }
    }
  }

  Timer { id: reconnectTimer; interval: 2000; running: false; repeat: false; onTriggered: ws.active = true }
  Timer { id: logsReconnect; interval: 2000; running: false; repeat: false; onTriggered: wsLogs.active = true }
}
