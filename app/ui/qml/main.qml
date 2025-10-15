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
import "shortcuts" as Keys
import "cores" as Cores
import "Api" as Api
import "Sockets"


App_Base {
  id: win

  // F11/F12 shortcuts
  Keys.ShortcutManager { id: keyMgr; rootWindow: win; onOpenTestPage: testPage.open() }

  // Init global API client
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

  // F12 dialog for test page
  Dialog {
    id: testPage
    modal: true
    x: 40; y: 40
    width: Math.min(parent ? parent.width-80 : 1200, 1200)
    height: Math.min(parent ? parent.height-80 : 800, 800)
    contentItem: Loader { source: "pages/main/test_page/TestPageView.qml" }
  }
}

