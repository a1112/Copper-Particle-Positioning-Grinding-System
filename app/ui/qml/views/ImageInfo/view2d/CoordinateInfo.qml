import QtQuick
import QtQuick.Controls

import "../../../cores" as Cores

Item {
  id: infoPanel
  property bool hoverValid: Cores.CoreDataView.cursorValid
  property point pixel: Cores.CoreDataView.cursorPixel
  property var camera: Cores.CoreDataView.cursorCamera
  property bool cameraValid: Cores.CoreDataView.cursorCameraValid
  property var machine: Cores.CoreDataView.cursorMachine

  visible: hoverValid
  implicitWidth: background.visible ? background.implicitWidth : 0
  implicitHeight: background.visible ? background.implicitHeight : 0
  width: implicitWidth
  height: implicitHeight

  Rectangle {
    id: background
    visible: infoPanel.hoverValid
    radius: 6
    color: Qt.rgba(0.05, 0.09, 0.15, 0.85)
    border.color: Qt.rgba(0.4, 0.7, 1.0, 0.6)
    border.width: 1
    implicitWidth: coordLabel.implicitWidth + 16
    implicitHeight: coordLabel.implicitHeight + 12
    width: implicitWidth
    height: implicitHeight

    Label {
      id: coordLabel
      anchors.centerIn: parent
      color: Cores.CoreStyle.text
      font.family: "monospace"
      text: infoPanel.hoverValid
            ? qsTr("像素 (%1, %2)\n相机 (%3, %4, %5) mm\n机床 (%6, %7, %8) mm")
                .arg(Math.round(infoPanel.pixel.x))
                .arg(Math.round(infoPanel.pixel.y))
                .arg(infoPanel.cameraValid && infoPanel.camera && !isNaN(infoPanel.camera.x) ? infoPanel.camera.x.toFixed(3) : "--")
                .arg(infoPanel.cameraValid && infoPanel.camera && !isNaN(infoPanel.camera.y) ? infoPanel.camera.y.toFixed(3) : "--")
                .arg(infoPanel.cameraValid && infoPanel.camera && !isNaN(infoPanel.camera.z) ? infoPanel.camera.z.toFixed(3) : "--")
                .arg(infoPanel.machine && !isNaN(infoPanel.machine.x) ? infoPanel.machine.x.toFixed(3) : "--")
                .arg(infoPanel.machine && !isNaN(infoPanel.machine.y) ? infoPanel.machine.y.toFixed(3) : "--")
                .arg(infoPanel.machine && !isNaN(infoPanel.machine.z) ? infoPanel.machine.z.toFixed(3) : "--")
            : qsTr("移动鼠标查看坐标")
    }
  }
}
