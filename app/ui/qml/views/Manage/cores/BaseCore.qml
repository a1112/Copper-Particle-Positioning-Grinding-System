import QtQuick

// Shared selection logic for manage view cores.
QtObject {
  id: root

  property var views: []
  property var selectedKeys: []
  property var selectedViews: []

  signal selectionChanged()

  function _asList(value) {
    if (Array.isArray(value))
      return value
    if (value === undefined || value === null)
      return []
    if (typeof value === "object" && value.length !== undefined) {
      var temp = []
      for (var i = 0; i < value.length; ++i)
        temp.push(value[i])
      return temp
    }
    return []
  }

  function isSelected(key) {
    if (!key)
      return false
    var keys = _asList(selectedKeys)
    return keys.indexOf(key) !== -1
  }

  function setSelected(key, enabled) {
    if (!key)
      return
    var keys = _asList(selectedKeys).slice()
    var index = keys.indexOf(key)
    if (enabled && index === -1) {
      keys.push(key)
      selectedKeys = keys
      updateSelected()
    } else if (!enabled && index !== -1) {
      keys.splice(index, 1)
      selectedKeys = keys
      updateSelected()
    }
  }

  function toggle(key) {
    setSelected(key, !isSelected(key))
  }

  function getView(key) {
    if (!key)
      return null
    var list = _asList(views)
    for (var i = 0; i < list.length; ++i) {
      if (list[i].key === key)
        return list[i]
    }
    return null
  }

  function updateSelected() {
    var list = _asList(views)
    var keys = _asList(selectedKeys)
    var next = []
    for (var i = 0; i < list.length; ++i) {
      var entry = list[i]
      if (keys.indexOf(entry.key) !== -1)
        next.push(entry)
    }
    selectedViews = next
    selectionChanged()
  }

  function resetSelection(keys) {
    if (!Array.isArray(keys) || !keys.length)
      return
    selectedKeys = keys.slice()
    updateSelected()
  }

  Component.onCompleted: updateSelected()
  onSelectedKeysChanged: updateSelected()
  onViewsChanged: updateSelected()
}
