import QtQuick.Controls
import "../../works" as Works

Menu {
  id: root
  property var dataEntryDialog: null

  title: qsTr("数据")

  MenuItem {
    text: qsTr("手动添加工件")
    onTriggered: {
      if (!root.dataEntryDialog)
        return
      if (root.dataEntryDialog.openWithReset)
        root.dataEntryDialog.openWithReset()
      else if (root.dataEntryDialog.open)
        root.dataEntryDialog.open()
    }
  }

  MenuItem {
    text: qsTr("刷新任务状态")
    onTriggered: Works.TaskWork.refresh()
  }
}
