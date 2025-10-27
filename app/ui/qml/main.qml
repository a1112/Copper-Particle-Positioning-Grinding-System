import QtCore
import QtQuick
import QtQuick.Window
import QtQuick.Layouts
import QtQuick.Controls.Material

import "pages"
import "pages/main"
import "dialogs"
import "menu"
import "menu/settings"
import "menu/states"
import "cores" as Cores
import "Api" as Api
import "datas" as Datas
import "works" as Works
import "test"
import "action"

App_Base {
  // 应用窗口实例
  id: win

  Component.onCompleted: {
    Api.ApiClient.root = win
    Api.ApiClient.showError = function(msg){ Cores.CoreError.showError(msg) }
    Api.ApiClient.setBase(Api.Urls.base())
    Works.Works.startAll()
  }

  // 主界面布局容器
  MainLayouts {
    anchors.fill: parent
  }

  DataEntryDialog { id: dataEntryDialog }
  GlobErrorDialog { id: errorDialog }
  TestImagesDialog { id: testDialog }
  SettingsDrawer { id: settingsDrawer }
  SettingPage{id: settingsPage}
  StatePage{id:statePage}
  TestWindow{id:testWindow}
  EstopDialog {id: estopDialog}
  Shortcuts {}
}







