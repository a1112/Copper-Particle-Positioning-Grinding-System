import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "./pages" as Pages

Item {
  id: root
  required property var statePageCore

  Layout.fillWidth: true
  Layout.fillHeight: true

  ColumnLayout {
    anchors.fill: parent
    spacing: 0

    TabBar {
      id: tabBar
      Layout.fillWidth: true

      TabButton { text: qsTr("任务队列") }
      TabButton { text: qsTr("命令列表") }
      TabButton { text: qsTr("采集图像预览") }
      TabButton { text: qsTr("路径预览") }
    }

    StackLayout {
      Layout.fillWidth: true
      Layout.fillHeight: true
      currentIndex: tabBar.currentIndex

      Pages.TaskStatusSummaryPage {
        statePageCore: root.statePageCore
      }

      Pages.TaskCommandListPage {
        statePageCore: root.statePageCore
      }

      Pages.TaskImagePreviewPage {
        statePageCore: root.statePageCore
      }

      Pages.TaskPathPreviewPage {
        statePageCore: root.statePageCore
      }
    }
  }
}
