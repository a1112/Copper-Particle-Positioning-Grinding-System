pragma Singleton
import QtQuick

QtObject {
  id: root
  property int status: -1
  property bool connected: false
  property var logs: []
  property int logsMax: 1000
  property string levelFilter: "ALL"
  property var filteredLogs: []
  signal logReceived(var item)

  function _levelRank(level) {
    var key = String(level || "").toUpperCase()
    switch (key) {
    case "TRACE":
      return 0
    case "DEBUG":
      return 1
    case "INFO":
      return 2
    case "WARN":
    case "WARNING":
      return 3
    case "ERROR":
      return 4
    default:
      return 2
    }
  }

  function matchesFilter(item) {
    return _matchesFilter(item)
  }

  function _matchesFilter(item) {
    if (!item)
      return false
    var filterKey = String(levelFilter || "ALL").toUpperCase()
    if (filterKey === "ALL")
      return true
    var itemRank = _levelRank(item.level !== undefined ? item.level : item.Level)
    var minRank = _levelRank(filterKey)
    return itemRank >= minRank
  }

  function updateFiltered() {
    var next = []
    for (var i = 0; i < logs.length; ++i) {
      var entry = logs[i]
      if (!entry)
        continue
      if (_matchesFilter(entry))
        next.push(entry)
    }
    filteredLogs = next
  }

  function clear() {
    logs = []
    filteredLogs = []
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

  onLevelFilterChanged: updateFiltered()
  onLogsChanged: updateFiltered()
}
