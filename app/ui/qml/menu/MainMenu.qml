import QtQuick.Controls
import QtQuick.Window
import "../datas" as Datas
import "./main_menus" as MainMenus

Menu {
  id: mainMenu

  readonly property string _recordRoot: "D:/SaveData/record"

  function openRecordFolder() {
    var recordId = Number(Datas.TaskDatas.latestRecordId || 0)
    var targetPath = _recordRoot
    if (recordId > 0)
      targetPath += "/" + recordId
    var normalized = targetPath.replace(/\\/g, "/")
    Qt.openUrlExternally("file:///" + normalized)
  }

  Menu {
    title: qsTr("文件")
    MenuItem {
      text: qsTr("打开保存位置")
      onTriggered: mainMenu.openRecordFolder()
    }
  }

  MainMenus.InterfaceMenu {
  }

  MenuItem {
    text: qsTr("刷新配置")
    enabled: settingsPage && settingsPage.loadSettings
    onTriggered: {
      if (settingsPage && settingsPage.loadSettings)
        settingsPage.loadSettings()
    }
  }

  MainMenus.ControlMenu { }

  MainMenus.DataMenu {
    dataEntryDialog: dataEntryDialog
  }

  MenuItem {
    text: qsTr("清除告警")
    onTriggered: {
      if (!errorDialog)
        return
      if (errorDialog.visible && errorDialog.close)
        errorDialog.close()
      else if (errorDialog.accept)
        errorDialog.accept()
    }
  }

  MenuSeparator { }

  MenuItem {
    text: (win && win.visibility === Window.FullScreen)
          ? qsTr("全屏")
          : qsTr("进入全屏")
    onTriggered: {
      if (!win)
        return
      if (win.visibility === Window.FullScreen)
        win.showMaximized()
      else
        win.showFullScreen()
    }
  }

  MenuItem {
    text: qsTr("调试窗口")
    onTriggered: {
      if (!testWindow)
        return
      testWindow.visible = !testWindow.visible
      if (testWindow.visible && testWindow.raise)
        testWindow.raise()
    }
  }

  MenuItem {
    text: qsTr("测试图像...")
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
