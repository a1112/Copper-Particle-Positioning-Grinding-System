pragma Singleton
import QtQuick
import QtCore

Item {
  id: root
  // 主界面当前选中的页签索引
  property int selectedTabIndex: 0

  // 当前运行模式索引
  property int currentRunModelIndex: 0
  // 当前运行模式名称
  readonly property string currentRunModelName: CoreUI.allRunModel[currentRunModelIndex]

  // 是否处于手动模式
  readonly property bool isUseModel: currentRunModelName == "手动"

  // 实时数据视图索引
  property int realViewIndex: 0
  // 实时数据视图名称
  readonly property string realViewName: CoreUI.dataViewModels[realViewIndex]

  Settings {
    id: st
    category: "CoreState"
    // 持久化需要记住的界面状态
    property alias selectedTabIndex: root.selectedTabIndex
    property alias currentRunModelIndex: root.currentRunModelIndex
  }
}
