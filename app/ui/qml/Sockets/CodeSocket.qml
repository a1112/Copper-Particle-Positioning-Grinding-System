pragma Singleton
import QtQuick
import QtWebSockets
import "../Api" as Api

// Code execution WebSocket singleton
Item {
  id: root
  readonly property bool connected: (wsCode.status===WebSocket.Open)
  property string runState: 'IDLE'
  property int currentIndex: -1
  property var lines: []  // program lines array of strings

  WebSocket {
    id: wsCode
    url: Api.Urls.wsCode()
    active: true
    onTextMessageReceived: function(message){
      try {
        var p = JSON.parse(message)
        if (p.type === 'program' && Array.isArray(p.lines)) {
          root.lines = p.lines
        } else if (p.type === 'state') {
          root.runState = p.state || 'IDLE'
          root.currentIndex = (p.current!==undefined ? p.current : -1)
        }
      } catch(e) { /* ignore */ }
    }
  }
}
