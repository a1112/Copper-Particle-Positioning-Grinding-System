pragma Singleton
import QtQuick

QtObject {
  id: root
  property int status: -1
  property bool connected: false
  property var logs: []
  property int logsMax: 1000
  signal logReceived(var item)

  function clear() {
    logs = []
  }

  function append(item) {
    if (!item)
      return
    logs.push(item)
    if (logs.length > logsMax)
      logs.shift()
    logReceived(item)
  }

  function appendMany(items) {
    if (!items || !items.length)
      return
    for (var i = 0; i < items.length; ++i)
      append(items[i])
  }
}
