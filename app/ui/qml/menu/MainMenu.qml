import QtQuick.Controls
import QtQuick.Window

Menu {
    Menu{
        title: qsTr("界面功能")
        MenuItem {
          text: qsTr("打开设置抽屉")
          visible: settingsDrawer && !settingsDrawer.visible
          onTriggered: settingsDrawer.open()
        }
        MenuItem {
          text: qsTr("配置中心…")
          onTriggered: settingsPage.open()
        }
    }
    MenuItem {
      text: qsTr("刷新配置")
      enabled: settingsPage && settingsPage.loadSettings
      onTriggered: {
        if (settingsPage && settingsPage.loadSettings)
          settingsPage.loadSettings()
      }
    }

    Menu{
        title: qsTr("控制")

    }

    MenuItem {
      text: qsTr("清除告警")
      onTriggered: {
        if (errorDialog) {
          if (errorDialog.visible && errorDialog.close)
            errorDialog.close()
          else if (errorDialog.accept)
            errorDialog.accept()
        }
      }
    }

    MenuSeparator { }

    MenuItem {
      text: (appWindow && appWindow.visibility === Window.FullScreen)
            ? qsTr("全屏")
            : qsTr("进入全屏")
      onTriggered: {
        if (!appWindow)
          return
        if (appWindow.visibility === Window.FullScreen)
          appWindow.showMaximized()
        else
          appWindow.showFullScreen()
      }
    }

    MenuItem {
      text:qsTr("调试窗口")
      onTriggered: {
        if (!testWindow)
          return
        testWindow.visible = !testWindow.visible
        if (testWindow.visible && testWindow.raise)
          testWindow.raise()
      }
    }

    MenuItem {
      text: qsTr("测试图像…")
      onTriggered: {
        if (testDialog && testDialog.open)
          testDialog.open()
      }
    }
    MenuSeparator { }
    MenuItem {
      text: qsTr("退出应用")
      onTriggered: Qt.quit()
    }
}
