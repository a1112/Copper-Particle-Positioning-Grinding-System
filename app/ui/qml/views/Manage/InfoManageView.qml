import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "head"

ColumnLayout {
  id: root
  spacing: 8

  InfoViewCore {
    id: infoCore
  }

  property InfoViewCore infoViewCore: infoCore

  InfoHeadView {
    Layout.fillWidth: true
    infoViewCore: infoCore
  }

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
        model: infoCore.selectedViews
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
