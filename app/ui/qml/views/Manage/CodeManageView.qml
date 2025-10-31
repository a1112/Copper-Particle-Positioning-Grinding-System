import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "head"
import "cores"
import "../Code"
import "mix"
// Make CodeManageView follow the same core-driven structure as InfoViewCore/InfoManageView
ColumnLayout {
  id: root
  spacing: 5

  property CodeViewCore codeCore: CodeViewCore{ }
  // Expose core if needed by consumers
  property var infoViewCore: codeCore

  // Head with filter menu, reusing existing components
  InfoHeadView {
    title: qsTr("运行")
    Layout.fillWidth: true
    infoViewCore: codeCore
  }

  // Content area: render selected views
  ScrollView {
    Layout.fillWidth: true
    height: flick.height
    Flickable {
      id: flick
      clip: true
      contentWidth: width
      contentHeight: columnContent.implicitHeight

      Column {
        id: columnContent
        width: flick.width
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
    }
    ScrollBar.vertical: ScrollBar { }
  }

  CodeTaskFlip{
      Layout.fillWidth: true
      Layout.fillHeight: true
  }
  CodeContorl{}
}
