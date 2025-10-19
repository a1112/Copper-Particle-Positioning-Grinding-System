import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "head"

// Make CodeManageView follow the same core-driven structure as InfoViewCore/InfoManageView
ColumnLayout {
  id: root
  spacing: 8

  // Core object providing selectable subviews (mirrors InfoViewCore API)
  QtObject {
    id: codeCore

    property var views: [
      {
        key: "codeEditor",
        title: qsTr("代码编辑器"),
        source: Qt.resolvedUrl("../Code/CodeView.qml")
      },
      {
        key: "codeControls",
        title: qsTr("运行控制"),
        source: Qt.resolvedUrl("../Code/CodeContorl.qml")
      }
    ]

    property var selectedKeys: ["codeEditor", "codeControls"]
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

    function toggle(key) { setSelected(key, !isSelected(key)) }

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

  // Expose core if needed by consumers
  property var infoViewCore: codeCore

  // Head with filter menu, reusing existing components
  InfoHeadView {
    Layout.fillWidth: true
    infoViewCore: codeCore
  }

  // Content area: render selected views
  ScrollView {
    Layout.fillWidth: true
    Layout.fillHeight: true
    contentWidth: availableWidth
    contentHeight: columnContent.implicitHeight

    Column {
      id: columnContent
      width: root.width
      spacing: 10

      Repeater {
        model: codeCore.selectedViews
        delegate: Loader {
          width: columnContent.width
          source: modelData.source
          asynchronous: true
          onLoaded: {
            if (item) {
              item.width = columnContent.width
              if (item.hasOwnProperty("Layout"))
                item.Layout.fillWidth = true
            }
          }
        }
      }
    }

    ScrollBar.vertical: ScrollBar { }
  }
}

