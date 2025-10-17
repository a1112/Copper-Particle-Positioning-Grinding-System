pragma Singleton
import QtQuick

QtObject {
  id: root
  property bool connected: false
  property var last: ({})
  readonly property real feedRate: Number((last && last.feed_rate) || 0)
  readonly property real downfeedTarget: Number((last && last.downfeed_target) || 0)
  readonly property real downfeedCurrent: Number((last && last.downfeed_current) || 0)
  readonly property real removalCurrent: Number((last && last.removal_current) || 0)
  readonly property real removalExpected: Number((last && last.removal_expected) || 0)
  readonly property real torqueMax: Number((last && last.torque_max) || 0)
  readonly property real torque: Number((last && last.torque) || 0)
  readonly property real elapsedSec: Number((last && last.elapsed_sec) || 0)

  function update(payload) {
    last = payload || ({})
  }

  function reset() {
    connected = false
    last = ({})
  }
}
