pragma Singleton
import QtQuick
import QtWebSockets
import "../Api" as Api

// Logs WebSocket singleton: history + append stream
Item {
  id: root
  readonly property int logsStatus: wsLogs.status
  readonly property bool logsConnected: (wsLogs.status===WebSocket.Open)
  property var logs: []            // array of {ts, time?, level, name, msg}
  property int logsMax: 1000
  signal logReceived(var item)

  function clearLogs(){ logs = [] }
  function addLocalLog(level, name, msg){ pushLog({ ts: Date.now()/1000.0, level: level||'INFO', name: name||'local', msg: msg||'' }) }
  function pushLog(item){ if (!item) return; logs.push(item); if (logs.length > logsMax) logs.shift(); logReceived(item) }
  function sendServerLog(msg){ Api.ApiClient.post('/test/log?msg=' + encodeURIComponent(msg||'UI log'), {}, function(_){}, function(s,m){ console.log('send log err', s, m) }) }
  function clearServerLogs(){ Api.ApiClient.post('/test/log/clear', {}, function(_){}, function(s,m){ console.log('clear logs err', s, m) }) }

  WebSocket {
    id: wsLogs
    url: Api.Urls.wsLogs()
    active: true
    onStatusChanged: function(status){ if (status === WebSocket.Error || status === WebSocket.Closed) { wsLogs.active = false; logsReconnect.restart() } }
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

  Timer { id: logsReconnect; interval: 2000; running: false; repeat: false; onTriggered: wsLogs.active = true }
}
