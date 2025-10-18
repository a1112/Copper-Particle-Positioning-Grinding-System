import QtQuick

QtObject {
  id: root

  property var views: [
    {
      key: "runState",
      title: qsTr("运行信息"),
      source: Qt.resolvedUrl("../DriveInfo/RunStateInfoView.qml")
    },
    {
      key: "driveMetrics",
      title: qsTr("运行数据"),
      source: Qt.resolvedUrl("../DriveInfo/DriveInfoView.qml")
    },
    {
      key: "toolInfo",
      title: qsTr("刀具信息"),
      source: Qt.resolvedUrl("../DriveInfo/ToolInfoView.qml")
    },
    {
      key: "torqueChart",
      title: qsTr("扭矩曲线"),
      source: Qt.resolvedUrl("../Charts/TorqueChart.qml")
    },
    {
      key: "elevationChart",
      title: qsTr("高度趋势"),
      source: Qt.resolvedUrl("../Charts/ElevationAreaChart.qml")
    }
  ]

  property var selectedKeys: ["driveMetrics", "runState"]
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
    if (!keys || !keys.length)
      return
    selectedKeys = keys.slice()
    updateSelected()
  }

  Component.onCompleted: updateSelected()
  onSelectedKeysChanged: updateSelected()
}
