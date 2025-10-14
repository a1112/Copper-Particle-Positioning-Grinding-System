import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../views/DriveInfo" as Drv
import "../../../views/ImageInfo" as Img
import "../../../views/Log" as Log
import "../../../views/Control" as Ctrl
import "../../../views/Code" as Code
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
      SplitView { SplitView.preferredWidth: 440; SplitView.fillHeight: true; orientation: Qt.Vertical
        Drv.DeviceMsgView{  SplitView.fillWidth: true; SplitView.preferredHeight: 160}
        Drv.DriveInfoView { SplitView.fillWidth: true; SplitView.preferredHeight: 420 }
      }
      // 中列：图像信息预览
      Img.ImageInfoView {
        SplitView.fillWidth: true
        SplitView.fillHeight: true
      }
      // 右列：程序/代码状态
      Code.CodeView{
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
      Charts.ElevationAreaChart { SplitView.fillHeight: true; SplitView.preferredWidth: 520; points: (elevPts.length?elevPts:demoPts); cuts: (elevCuts.length?elevCuts:demoCuts); base: 0.0 }
      Ctrl.PTZControl {
        SplitView.fillHeight: true
        SplitView.preferredWidth: 400
      }
    }
  }
}






