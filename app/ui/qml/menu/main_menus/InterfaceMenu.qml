import QtQuick.Controls

Menu {
  id: root
  property var settingsDrawer: null
  property var settingsPage: null

  title: qsTr("界面功能")

  MenuItem {
    text: qsTr("打开设置抽屉")
    visible: root.settingsDrawer && !root.settingsDrawer.visible
    onTriggered: {
      if (root.settingsDrawer && root.settingsDrawer.open)
        root.settingsDrawer.open()
    }
  }

  MenuItem {
    text: qsTr("配置中心...")
    onTriggered: {
      if (root.settingsPage && root.settingsPage.open)
        root.settingsPage.open()
    }
  }
}
