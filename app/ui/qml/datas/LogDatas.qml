pragma Singleton
import QtQuick

Item {
  id: root

  property int status: -1
  property bool connected: false
  property int logsMax: 1000
  property string levelFilter: "ALL"

  ListModel { id: logsModel }
  ListModel { id: filteredModel }

  property alias logs: logsModel
  property alias filteredLogs: filteredModel

  property int nextId: 0

  signal logReceived(var item)
  signal filteredAboutToUpdate()
  signal filteredUpdated()

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

  function _normalizeEntry(entry) {
    if (entry === undefined || entry === null)
      return null
    if (typeof entry === "object") {
      var clone = {}
      for (var key in entry) {
        if (!entry.hasOwnProperty || entry.hasOwnProperty(key))
          clone[key] = entry[key]
      }
      return clone
    }
    return { value: entry }
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
    var rawLevel = item.level !== undefined ? item.level : item.Level
    var itemRank = _levelRank(rawLevel)
    var minRank = _levelRank(filterKey)
    return itemRank >= minRank
  }

  function clear() {
    filteredAboutToUpdate()
    logsModel.clear()
    filteredModel.clear()
    filteredUpdated()
  }

  function _removeFromFilteredById(targetId, notifyChange) {
    for (var i = 0; i < filteredModel.count; ++i) {
      var row = filteredModel.get(i)
      if (row && row.__id === targetId) {
        if (notifyChange)
          notifyChange()
        filteredModel.remove(i)
        return true
      }
    }
    return false
  }

  function _trimToMax(notifyChange) {
    var changed = false
    while (logsModel.count > logsMax && logsModel.count > 0) {
      var removed = logsModel.get(0)
      var removedId = removed && removed.__id
      logsModel.remove(0)
      if (_removeFromFilteredById(removedId, notifyChange))
        changed = true
    }
    return changed
  }

  function rebuildFiltered() {
    filteredModel.clear()
    for (var i = 0; i < logsModel.count; ++i) {
      var entry = logsModel.get(i)
      if (_matchesFilter(entry))
        filteredModel.append(entry)
    }
  }

  function updateFiltered() {
    filteredAboutToUpdate()
    rebuildFiltered()
    filteredUpdated()
  }

  function append(item) {
    var normalized = _normalizeEntry(item)
    if (!normalized)
      return
    normalized.__id = nextId++
    logsModel.append(normalized)
    var aboutEmitted = false
    var changed = false
    function ensureAbout() {
      if (!aboutEmitted) {
        filteredAboutToUpdate()
        aboutEmitted = true
      }
    }
    if (_matchesFilter(normalized)) {
      ensureAbout()
      filteredModel.append(normalized)
      changed = true
    }
    if (_trimToMax(ensureAbout))
      changed = true
    if (changed)
      filteredUpdated()
    logReceived(normalized)
  }

  function appendMany(items) {
    if (!items || !items.length)
      return
    var last = null
    var aboutEmitted = false
    var changed = false
    function ensureAbout() {
      if (!aboutEmitted) {
        filteredAboutToUpdate()
        aboutEmitted = true
      }
    }
    for (var i = 0; i < items.length; ++i) {
      var entry = _normalizeEntry(items[i])
      if (!entry)
        continue
      entry.__id = nextId++
      logsModel.append(entry)
      if (_matchesFilter(entry)) {
        ensureAbout()
        filteredModel.append(entry)
        changed = true
      }
      last = entry
    }
    if (_trimToMax(ensureAbout))
      changed = true
    if (changed)
      filteredUpdated()
    if (last !== null)
      logReceived(last)
  }

  onLevelFilterChanged: updateFiltered()
  onLogsMaxChanged: {
    var aboutEmitted = false
    function ensureAbout() {
      if (!aboutEmitted) {
        filteredAboutToUpdate()
        aboutEmitted = true
      }
    }
    var trimmed = _trimToMax(ensureAbout)
    if (!aboutEmitted)
      filteredAboutToUpdate()
    rebuildFiltered()
    filteredUpdated()
  }
}
