import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../views/DriveInfo" as Drv
import "../../../views/ImageInfo" as Img
import "../../../views/Log" as Log
import "../../../views/Code" as Code
// 设备信息 + 图像信息 预览页
Item {
  id: root
  anchors.fill: parent
  SplitView{
    anchors.fill: parent
    orientation: Qt.Vertical
    SplitView {
      id: rootSplit
      SplitView.fillWidth: true
      SplitView.fillHeight: true
      orientation: Qt.Horizontal

      // 顶部：设备状态/驱动信息
      Drv.DriveInfoView {
        SplitView.preferredWidth: 400
        SplitView.fillHeight: true

      }

      // 底部：图像信息预览
      Img.ImageInfoView {
        SplitView.fillWidth: true
        SplitView.fillHeight: true
      }
      Code.CodeView{
        SplitView.fillHeight: true
        SplitView.preferredWidth: 500
      }
    }
    SplitView{
              SplitView.fillWidth: true
              SplitView.preferredHeight: 300
      Log.LogView{
        SplitView.fillHeight: true

      }

    }
  }
}
