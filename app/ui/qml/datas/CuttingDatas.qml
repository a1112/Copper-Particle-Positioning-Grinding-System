pragma Singleton
import QtQuick
// Cutting payload fields documented in docs/ui_data_contracts.md

QtObject {
  id: root
  property bool connected: false
  property var last: ({})
  readonly property real feedRate: (last && last.feed_rate !== undefined) ? Number(last.feed_rate) : 0
  readonly property real downfeedTarget: (last && last.downfeed_target !== undefined) ? Number(last.downfeed_target) : 0
  readonly property real downfeedCurrent: (last && last.downfeed_current !== undefined) ? Number(last.downfeed_current) : 0
  readonly property real removalCurrent: (last && last.removal_current !== undefined) ? Number(last.removal_current) : 0
  readonly property real removalExpected: (last && last.removal_expected !== undefined) ? Number(last.removal_expected) : 0
  readonly property real removalRemaining: Math.max(0, removalExpected - removalCurrent)
  readonly property real torqueMax: (last && last.torque_max !== undefined) ? Number(last.torque_max) : 0
  readonly property real torque: (last && last.torque !== undefined) ? Number(last.torque) : 0
  readonly property real elapsedSec: (last && last.elapsed_sec !== undefined) ? Number(last.elapsed_sec) : 0

  function update(payload) {
    if (!payload)
      return
    connected = true
    last = payload
  }

  function reset() {
    connected = false
    last = ({})
  }
}
