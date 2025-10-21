import QtQuick

// Core object providing selectable subviews (mirrors InfoViewCore API)
QtObject {
  id: codeCore

  property var views: [

    {
      key: "cuttingStats",
      title: qsTr("切削统计"),
      source: Qt.resolvedUrl("../DriveInfo/CuttingStatisticsView.qml")
    },
    {
      key: "singleCutStatus",
      title: qsTr("单次切削状态"),
      source: Qt.resolvedUrl("../DriveInfo/SingleCutCommandStatusView.qml")
    },
    {
      key: "codeEditor",
      title: qsTr("代码编辑"),
      source: Qt.resolvedUrl("../Code/CodeView.qml")
    },
    {
      key: "codeControls",
      title: qsTr("运行控制"),
      source: Qt.resolvedUrl("../Code/CodeContorl.qml")
    },
  ]

  property var selectedKeys: ["codeEditor", "codeControls", "cuttingStats", "singleCutStatus"]
  property var selectedViews: []

  signal selectionChanged()

  function isSelected(key) {
    if (!key)
      return false
    return selectedKeys.indexOf(key) !== -1
  }

  function setSelected(key, enabled) {
    if (!key)
      return
    var idx = selectedKeys.indexOf(key)
    if (enabled && idx === -1) {
      var next = selectedKeys.slice()
      next.push(key)
      selectedKeys = next
      updateSelected()
    } else if (!enabled && idx !== -1) {
      var removed = selectedKeys.slice()
      removed.splice(idx, 1)
      selectedKeys = removed
      updateSelected()
    }
  }

  function toggle(key) {
    setSelected(key, !isSelected(key))
  }

  function getView(key) {
    for (var i = 0; i < views.length; ++i) {
      if (views[i].key === key)
        return views[i]
    }
    return null
  }

  function updateSelected() {
    var next = []
    for (var i = 0; i < views.length; ++i) {
      var entry = views[i]
      if (selectedKeys.indexOf(entry.key) !== -1)
        next.push(entry)
    }
    selectedViews = next
    selectionChanged()
  }

  function resetSelection(keys) {
    if (!keys)
      return
    if (!keys.length)
      return
    selectedKeys = keys.slice()
    updateSelected()
  }

  Component.onCompleted: updateSelected()
  onSelectedKeysChanged: updateSelected()
}
