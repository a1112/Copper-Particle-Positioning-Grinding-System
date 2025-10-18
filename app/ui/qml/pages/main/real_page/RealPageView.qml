import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../views/Manage" as Manage
import "../../../views/ImageInfo" as Img
import "../../../views/Log" as Log
import "../../../views/Control" as Ctrl
import "../../../views/Charts" as Charts
import "../../../Api" as Api

// 设备信息 + 图像信息 预览页
Item {
  id: root
  Layout.fillWidth: true
  Layout.fillHeight: true


  SplitView {
    anchors.fill: parent
    orientation: Qt.Vertical

    SplitView {
      id: rootSplit
      SplitView.fillWidth: true
      SplitView.fillHeight: true
      orientation: Qt.Horizontal

      // 左列：设备状态/信息 + 元数据
      Manage.InfoManageView{
        SplitView.preferredWidth: 440
        SplitView.fillHeight: true
      }

      // // 中列：图像信息预览
      Img.ImageInfoView {
        SplitView.fillWidth: true
        SplitView.fillHeight: true
      }

      // 右列：程序/代码状态
      Manage.CodeManageView{
        SplitView.fillHeight: true
        SplitView.preferredWidth: 500
      }
    }

    SplitView {
      SplitView.fillWidth: true
      SplitView.preferredHeight: 280
      Log.LogView {
        SplitView.fillHeight: true
        SplitView.fillWidth: true
      }
      Charts.ElevationAreaChart {
        SplitView.fillHeight: true
        SplitView.preferredWidth: 520
      }
      Ctrl.PTZControl {
        SplitView.fillHeight: true
        SplitView.preferredWidth: 400
      }
    }
  }
}








