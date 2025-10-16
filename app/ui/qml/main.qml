import QtCore
import QtQuick
import QtQuick.Window
import QtQuick.Layouts
import QtQuick.Controls.Material

import "pages"
import "pages/main"
import "Dialogs"
import "menu"
import "menu/settings"
import "cores" as Cores
import "Api" as Api
import "Sockets"


App_Base {
  id: win

  // F11/F12 shortcuts
  Component.onCompleted: {
    Api.ApiClient.root = win
    Api.ApiClient.showError = function(msg){ Cores.CoreError.showError(msg) }
    Api.ApiClient.setBase(Api.Urls.base())
  }

  // Use MainLayouts as the top-level container
  MainLayouts { anchors.fill: parent }

  GlobErrorDialog { id: errorDialog }
  TestImagesDialog { id: testDialog }
  SettingsDrawer { id: settingsDrawer }
  SettingPage{id: settingsPage}
}

