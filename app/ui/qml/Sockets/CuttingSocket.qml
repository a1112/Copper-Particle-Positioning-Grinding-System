pragma Singleton
import QtQuick
import QtWebSockets
import "../Api" as Api

// Cutting metrics WebSocket singleton
Item {
  id: root
  // Last frame
  property var last: ({})
  // Convenience properties
  readonly property real feedRate: (last && last.feed_rate) || 0
  readonly property real downfeedTarget: (last && last.downfeed_target) || 0
  readonly property real downfeedCurrent: (last && last.downfeed_current) || 0
  readonly property real removalCurrent: (last && last.removal_current) || 0
  readonly property real removalExpected: (last && last.removal_expected) || 0
  readonly property real torqueMax: (last && last.torque_max) || 0
  readonly property real torque: (last && last.torque) || 0
  readonly property real elapsedSec: (last && last.elapsed_sec) || 0

  readonly property bool connected: (ws.status===WebSocket.Open)

  WebSocket {
    id: ws
    url: Api.Urls.base().replace('http://','ws://') + '/ws/cutting'
    active: true
    onStatusChanged: function(status){ /* bind */ }
    onTextMessageReceived: function(message){ try { root.last = JSON.parse(message) } catch(e){} }
  }
}
