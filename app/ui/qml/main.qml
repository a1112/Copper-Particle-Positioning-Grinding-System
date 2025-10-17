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
import "cores" as Cores
import "Api" as Api
import "datas" as Datas
import "works" as Works
import "test"

App_Base {
  id: win
  Material.theme: Material.Dark
  Component.onCompleted: {
    Api.ApiClient.root = win
    Api.ApiClient.showError = function(msg){ Cores.CoreError.showError(msg) }
    Api.ApiClient.setBase(Api.Urls.base())
    Works.StatusWork.start()
    Works.LogsWork.start()
    Works.CodeWork.start()
    Works.CuttingWork.start()
  }

  // Use MainLayouts as the top-level container
  MainLayouts { anchors.fill: parent }

  GlobErrorDialog { id: errorDialog }
  TestImagesDialog { id: testDialog }
  SettingsDrawer { id: settingsDrawer }
  SettingPage{id: settingsPage}
  TestWindow{id:testWindow}
}

