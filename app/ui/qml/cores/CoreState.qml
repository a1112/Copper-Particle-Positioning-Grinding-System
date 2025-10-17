pragma Singleton
import QtQuick
import QtCore

Item {
  id: root
  // Last selected main view tab
  property int selectedTabIndex: 0

  // 选择的自动模式
  property int currentRunModelIndex: 0
  readonly property string currentRunModelName: CoreUI.allRunModel[currentRunModelIndex]


  property int realViewIndex: 0
  Settings {
    id: st
    category: "CoreState"
    // Persist fields
    property alias selectedTabIndex: root.selectedTabIndex
    property alias currentRunModelIndex: root.currentRunModelIndex
  }
}

