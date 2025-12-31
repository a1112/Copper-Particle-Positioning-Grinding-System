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
import "dialogs/calibration" as CalibrationDialogs

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
  Shortcuts {}
  DataEntryDialog { id: dataEntryDialog }
  GlobErrorDialog { id: errorDialog }
  TestImagesDialog { id: testDialog }   //
  HistoryDrawer { id: historyDrawer }   // 历史记录抽屉
  SettingsDrawer { id: settingsDrawer } // 设置抽屉
  SettingPage{id: settingsPage}         // 配置中心
  StatePage{id:statePage}               // 状态中心
  TestWindow{id:testWindow}             // 测试
  EstopDialog {id: estopDialog}         // 急停弹窗
  CalibrationDialogs.CalibrationDialog { id: calibrationDialog } // 标定设置

  MainLayouts {
    anchors.fill: parent
  }


}







