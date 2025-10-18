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
  Component.onCompleted: {
    Api.ApiClient.root = win
    Api.ApiClient.showError = function(msg){ Cores.CoreError.showError(msg) }
    Api.ApiClient.setBase(Api.Urls.base())
    Works.Works.startAll()
  }

  // Use MainLayouts as the top-level container
  MainLayouts { anchors.fill: parent }

  GlobErrorDialog { id: errorDialog }
  TestImagesDialog { id: testDialog }
  SettingsDrawer { id: settingsDrawer }
  SettingPage{id: settingsPage}
  TestWindow{id:testWindow}

  /*
InfoViewCore 编码出现问题 增加 CodeManageView.qml 用于管理与切削运行相关的信息，框架与InfoManageView.qml 保持基本
  致，从上到下依次为 切削统计（对于这块板的）（粒子总量，切削量，剩余，平面高度，总耗时，预计剩余，最大扭矩，最大
  速），单次切削统计（切削深度，起始坐标，终点坐标，指令信息），指令表（已有），开始 执行（半自动可用）。停止 执行按
*/
}



