import QtQuick
import QtQuick.Controls

import "../../../cores" as Cores

Item {
  id: overlay
  anchors.fill: parent

  property point hoverPixel: Cores.CoreDataView.cursorPixel
  property var machineCoord: Cores.CoreDataView.cursorMachine
  property bool hoverValid: Cores.CoreDataView.cursorValid
  property var cameraCoord: Cores.CoreDataView.cursorCamera
  property bool cameraValid: Cores.CoreDataView.cursorCameraValid
  property real scaleX: 1.0
  property real scaleY: 1.0

  function requestUpdate() { cross.requestPaint() }

  onHoverPixelChanged: requestUpdate()
  onHoverValidChanged: requestUpdate()
  onScaleXChanged: requestUpdate()
  onScaleYChanged: requestUpdate()

  Canvas {
    id: cross
    anchors.fill: parent
    onPaint: {
      var ctx = getContext("2d")
      ctx.clearRect(0, 0, width, height)
      if (!overlay.hoverValid)
        return
      var px = overlay.hoverPixel.x * overlay.scaleX
      var py = overlay.hoverPixel.y * overlay.scaleY
      ctx.save()
      ctx.strokeStyle = "#22c55e"
      ctx.lineWidth = 1
      if (ctx.setLineDash)
        ctx.setLineDash([4, 4])
      ctx.beginPath()
      ctx.moveTo(px, 0)
      ctx.lineTo(px, height)
      ctx.moveTo(0, py)
      ctx.lineTo(width, py)
      ctx.stroke()
      ctx.restore()
      ctx.fillStyle = "#f97316"
      ctx.beginPath()
      ctx.arc(px, py, 3.5, 0, Math.PI * 2)
      ctx.fill()
    }
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
  }

  Rectangle {
    id: labelBackground
    visible: overlay.hoverValid
    radius: 6
    color: Qt.rgba(0.05, 0.09, 0.15, 0.85)
    border.color: Qt.rgba(0.4, 0.7, 1.0, 0.6)
    border.width: 1
    anchors.margins: 8
    anchors.left: parent.left
    anchors.top: parent.top
    implicitWidth: coordLabel.implicitWidth + 16
    implicitHeight: coordLabel.implicitHeight + 12

    Label {
      id: coordLabel
      anchors.centerIn: parent
      color: Cores.CoreStyle.text
      font.family: "monospace"
      text: overlay.hoverValid
            ? qsTr("像素 (%1, %2)\n相机 (%3, %4, %5) mm\n机床 (%6, %7, %8) mm")
                .arg(Math.round(overlay.hoverPixel.x))
                .arg(Math.round(overlay.hoverPixel.y))
                .arg(overlay.cameraValid && !isNaN(overlay.cameraCoord.x) ? overlay.cameraCoord.x.toFixed(3) : "--")
                .arg(overlay.cameraValid && !isNaN(overlay.cameraCoord.y) ? overlay.cameraCoord.y.toFixed(3) : "--")
                .arg(overlay.cameraValid && !isNaN(overlay.cameraCoord.z) ? overlay.cameraCoord.z.toFixed(3) : "--")
                .arg(overlay.machineCoord && !isNaN(overlay.machineCoord.x) ? overlay.machineCoord.x.toFixed(3) : "--")
                .arg(overlay.machineCoord && !isNaN(overlay.machineCoord.y) ? overlay.machineCoord.y.toFixed(3) : "--")
                .arg(overlay.machineCoord && !isNaN(overlay.machineCoord.z) ? overlay.machineCoord.z.toFixed(3) : "--")
            : qsTr("移动鼠标查看坐标")
    }
  }
}
