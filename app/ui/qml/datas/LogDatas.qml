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
    var next = logs.slice()
    next.push(item)
    if (next.length > logsMax)
      next = next.slice(next.length - logsMax)
    logs = next
    logReceived(item)
  }

  function appendMany(items) {
    if (!items || !items.length)
      return
    var next = logs.slice()
    var lastAppended = null
    for (var i = 0; i < items.length; ++i) {
      var entry = items[i]
      if (!entry)
        continue
      next.push(entry)
      lastAppended = entry
      if (next.length > logsMax)
        next.shift()
    }
    logs = next
    if (lastAppended !== null)
      logReceived(lastAppended)
  }
}
