import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../views/DriveInfo" as Drv
import "../../../views/ImageInfo" as Img

// 设备信息 + 图像信息 预览页
Item {
  id: root
  anchors.fill: parent

  SplitView {
    id: rootSplit
    anchors.fill: parent
    orientation: Qt.Vertical

    // 顶部：设备状态/驱动信息
    Drv.DriveInfoView {
      SplitView.fillWidth: true
      SplitView.preferredHeight: 280
    }

    // 底部：图像信息预览
    Img.ImageInfoView {
      SplitView.fillWidth: true
      SplitView.preferredHeight: 360
    }
  }
}
