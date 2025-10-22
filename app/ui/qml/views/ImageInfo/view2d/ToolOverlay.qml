import QtQuick
import QtQuick.Controls

import "../../../cores" as Cores

Item {
  id: overlay
  anchors.fill: parent

  property var toolWorldPosition: ({})
  property real pixelSizeMm: 0.2
  property real scaleX: 1.0
  property real scaleY: 1.0
  property real imageWidth: 640
  property real imageHeight: 360
  property var calibrationCore: null

  readonly property bool hasTool: toolWorldPosition && toolWorldPosition.x !== undefined && toolWorldPosition.y !== undefined
  readonly property point toolPixelPoint: {
    if (!hasTool)
      return Qt.point(-1, -1)
    if (calibrationCore && calibrationCore.worldToImage !== undefined) {
      var mapped = calibrationCore.worldToImage(toolWorldPosition)
      return Qt.point(mapped.x, mapped.y)
    }
    if (pixelSizeMm <= 0)
      return Qt.point(-1, -1)
    return Qt.point(toolWorldPosition.x / pixelSizeMm, toolWorldPosition.y / pixelSizeMm)
  }
  readonly property real toolPixelX: toolPixelPoint.x
  readonly property real toolPixelY: toolPixelPoint.y
  readonly property bool toolVisible: hasTool
      && toolPixelX >= 0 && toolPixelX <= imageWidth
      && toolPixelY >= 0 && toolPixelY <= imageHeight

  function requestUpdate() { toolCross.requestPaint() }

  onToolWorldPositionChanged: requestUpdate()
  onPixelSizeMmChanged: requestUpdate()
  onScaleXChanged: requestUpdate()
  onScaleYChanged: requestUpdate()
  onImageWidthChanged: requestUpdate()
  onImageHeightChanged: requestUpdate()
  onToolVisibleChanged: requestUpdate()
  onCalibrationCoreChanged: requestUpdate()

  Rectangle {
    id: marker
    visible: overlay.toolVisible
    width: 12
    height: 12
    radius: 6
    color: "#f87171"
    border.color: "#ffffff"
    border.width: 1.5
    x: overlay.toolPixelX * overlay.scaleX - width / 2
    y: overlay.toolPixelY * overlay.scaleY - height / 2
  }

  Canvas {
    id: toolCross
    anchors.fill: parent
    visible: overlay.toolVisible
    onPaint: {
      var ctx = getContext("2d")
      ctx.clearRect(0, 0, width, height)
      if (!overlay.toolVisible)
        return
      var px = overlay.toolPixelX * overlay.scaleX
      var py = overlay.toolPixelY * overlay.scaleY
      ctx.strokeStyle = "#f87171"
      ctx.lineWidth = 1.2
      ctx.beginPath()
      ctx.moveTo(px - 12, py)
      ctx.lineTo(px + 12, py)
      ctx.moveTo(px, py - 12)
      ctx.lineTo(px, py + 12)
      ctx.stroke()
    }
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
  }

  Rectangle {
    visible: overlay.toolVisible
    radius: 6
    color: Qt.rgba(0.1, 0.04, 0.04, 0.85)
    border.color: Qt.rgba(1, 0.55, 0.55, 0.7)
    border.width: 1
    anchors.margins: 8
    anchors.right: parent.right
    anchors.top: parent.top
    implicitWidth: toolLabel.implicitWidth + 16
    implicitHeight: toolLabel.implicitHeight + 12

    Label {
      id: toolLabel
      anchors.centerIn: parent
      font.family: "monospace"
      color: Cores.CoreStyle.text
      text: overlay.toolVisible
            ? qsTr("刀具坐标: %1 mm, %2 mm")
                .arg(toolWorldPosition.x.toFixed(3))
                .arg(toolWorldPosition.y.toFixed(3))
            : ""
    }
  }
}
