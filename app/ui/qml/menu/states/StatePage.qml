import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../cores" as Cores

Popup {
    property StatePageCore statePageCore: StatePageCore {}

  id: root
  modal: true
  dim: true
  focus: true
  padding: 0
  anchors.centerIn: parent
  width: parent ? Math.min(parent.width * 0.85, 1480) : 1180
  height: parent ? Math.min(parent.height * 0.9, 860) : 680
  closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

  background: Rectangle {
    radius: 14
    color: Cores.CoreStyle.surface
    border.color: Cores.CoreStyle.border
    border.width: 1
  }

  Component.onCompleted: statePageCore.refreshData()
  onOpened: statePageCore.refreshData()

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 24
    spacing: 5

    StatePageHead { statePageCore: root.statePageCore }
    StatePageInfo { statePageCore: root.statePageCore }

    TabBar {
      id: tabBar
      Layout.fillWidth: true
      TabButton { text: qsTr("任务状态") }
      TabButton { text: qsTr("报警处理") }
    }

    StackLayout {
      Layout.fillWidth: true
      Layout.fillHeight: true
      currentIndex: tabBar.currentIndex

      TaskStatusPanel {
      }

      AlarmPanel {
        statePageCore: root.statePageCore
      }
    }
  }

  BusyIndicator {
    anchors.centerIn: parent
    running: statePageCore.refreshing
    visible: statePageCore.refreshing
    z: 3
  }
}
