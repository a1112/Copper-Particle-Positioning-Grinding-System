import QtCore
import QtQuick.Layouts
import QtQuick.Controls.Material
import QtQuick
import QtQuick.Window



import "pages"
import "cores"
import "Dialogs"
import "Api"
import "Sockets"

App_Base {
  id: win
  property Core core: Core{}
  property CoreError coreError: CoreError{}
  property CoreSettings coreSettings: CoreSettings{}
  property CoreTimer coreTimer: CoreTimer{}

  property SocketsManage socketsManage: SocketsManage{}

  property ApiClient api: ApiClient{
    root: win
    showError: function(msg){ coreError.showError(msg) }
  }

  MainLayouts {
    id: layouts
    anchors.fill: parent
  }

  GlobErrorDialog{
    //全局弹窗
    id:errorDialog
  }

  TestImagesDialog {
    id: testDialog
  }

}


