import QtQuick.Controls
import "../../datas" as Datas
import "./" as MainMenus

Menu {
  title: qsTr("控制")

  MenuItem {
    text: checked
          ? qsTr("已解锁按钮（点击恢复锁定）")
          : qsTr("允许所有按钮点击（调试）")
    checkable: true
    checked: Datas.StatusDatas.forceEnableControls
    onTriggered: Datas.StatusDatas.forceEnableControls = checked
  }

  MainMenus.ManualControlMenu { }
}
