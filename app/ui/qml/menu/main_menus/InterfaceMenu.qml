import QtQuick.Controls

Menu {
  id: root
  title: qsTr("界面功能")
  MenuItem {
    text: qsTr("设置抽屉")
    onTriggered: {
      settingsDrawer.open()
    }
  }

  MenuItem {
    text: qsTr("配置中心")
    onTriggered: {
      settingsPage.open()
    }
  }
  MenuItem {
    text: qsTr("状态中心")
    onTriggered: {
      statePage.open()
    }
  }

  MenuItem {
    text: qsTr("标定设置")
    onTriggered: {
      if (calibrationDialog && calibrationDialog.openDialog)
        calibrationDialog.openDialog()
    }
  }
}
