import QtQuick
import QtWebSockets
Item {
    WebSocket {
      id: ws
      url: 'ws://' + coreSettings.apiHost + ':' + coreSettings.apiPort + '/ws'
      active: true
      onStatusChanged: function(status) {
        if (status === WebSocket.Error) {
          coreError.showError("WS 连接错误: " + errorString)
          ws.active = false; reconnectTimer.restart()
        } else if (status === WebSocket.Closed) {
          ws.active = false; reconnectTimer.restart()
        }
      }

      onTextMessageReceived: function(message) {
        try {
          var st = JSON.parse(message)
          lastMsgTs = Date.now()
          if (!st || !st.position) return
          backend._status = 'State: ' + st.state + ' | X ' + Number(st.position.x||0).toFixed(2) + ' Y ' + Number(st.position.y||0).toFixed(2)
          backend.statusChanged()
        } catch(e) { console.log('WS parse error:', e) }
      }
    }

    Timer { id: reconnectTimer; interval: 2000; running: false; repeat: false; onTriggered: ws.active = true }

}
