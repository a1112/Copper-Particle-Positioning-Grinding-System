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

  function _asNumber(value) {
    var num = Number(value)
    return isFinite(num) ? num : Number.NaN
  }

  function _toolWorldPoint(offsetX) {
    if (!hasTool)
      return null
    var baseX = _asNumber(toolWorldPosition.x)
    var baseY = _asNumber(toolWorldPosition.y)
    var point = {
      x: baseX + (offsetX || 0),
      y: baseY
    }
    var zVal = _asNumber(toolWorldPosition.z)
    if (isFinite(zVal))
      point.z = zVal
    return point
  }

  readonly property bool hasTool: toolWorldPosition
      && isFinite(_asNumber(toolWorldPosition.x))
      && isFinite(_asNumber(toolWorldPosition.y))

  readonly property point toolPixelPoint: {
    if (!hasTool)
      return Qt.point(-1, -1)
    if (calibrationCore && calibrationCore.worldToImage !== undefined) {
      var mapped = calibrationCore.worldToImage(_toolWorldPoint(0))
      if (!mapped || mapped.x === undefined || mapped.y === undefined)
        return Qt.point(-1, -1)
      return Qt.point(mapped.x, mapped.y)
    }
    if (pixelSizeMm <= 0)
      return Qt.point(-1, -1)
    return Qt.point(_asNumber(toolWorldPosition.x) / pixelSizeMm,
                    _asNumber(toolWorldPosition.y) / pixelSizeMm)
  }
  readonly property real toolPixelX: toolPixelPoint.x
  readonly property real toolPixelY: toolPixelPoint.y
  readonly property bool toolVisible: hasTool
      && toolPixelX >= 0 && toolPixelX <= imageWidth
      && toolPixelY >= 0 && toolPixelY <= imageHeight
  readonly property real toolDiameterMm: {
    if (!toolWorldPosition || toolWorldPosition.diameter === undefined)
      return Number.NaN
    var diameter = Number(toolWorldPosition.diameter)
    return diameter > 0 && isFinite(diameter) ? diameter : Number.NaN
  }
  readonly property real toolCircleRadius: {
    if (!toolVisible || !(toolDiameterMm > 0))
      return 0
    var diameterPx = _toolImageDiameter()
    if (!(diameterPx > 0))
      return 0
    var viewScale = (overlay.scaleX + overlay.scaleY) * 0.5
    if (!(viewScale > 0))
      viewScale = 1
    return diameterPx * viewScale / 2
  }

  function _toolImageDiameter() {
    if (!(toolDiameterMm > 0) || !hasTool)
      return 0
    if (calibrationCore && calibrationCore.worldToImage !== undefined) {
      var half = toolDiameterMm / 2
      var base = calibrationCore.worldToImage(_toolWorldPoint(0))
      if (!base || base.x === undefined || base.y === undefined)
        return 0
      var forward = calibrationCore.worldToImage(_toolWorldPoint(half))
      var backward = calibrationCore.worldToImage(_toolWorldPoint(-half))
      if (!forward || !backward || forward.x === undefined || backward.x === undefined)
        return 0
      return Math.abs(_asNumber(forward.x) - _asNumber(backward.x))
    }
    if (pixelSizeMm > 0)
      return toolDiameterMm / pixelSizeMm
    return 0
  }

  function requestUpdate() {
    toolCross.requestPaint()
    toolCircle.requestPaint()
  }

  function _formatNumber(value, decimals) {
    var num = Number(value)
    if (!isFinite(num))
      return "-"
    var precision = (decimals !== undefined) ? decimals : 3
    return num.toFixed(precision)
  }

  onToolWorldPositionChanged: requestUpdate()
  onPixelSizeMmChanged: requestUpdate()
  onScaleXChanged: requestUpdate()
  onScaleYChanged: requestUpdate()
  onImageWidthChanged: requestUpdate()
  onImageHeightChanged: requestUpdate()
  onToolVisibleChanged: requestUpdate()
  onCalibrationCoreChanged: requestUpdate()

  Canvas {
    id: toolCircle
    anchors.fill: parent
    visible: overlay.toolVisible && overlay.toolCircleRadius > 0
    onPaint: {
      var ctx = getContext("2d")
      ctx.clearRect(0, 0, width, height)
      if (!visible)
        return
      var px = overlay.toolPixelX * overlay.scaleX
      var py = overlay.toolPixelY * overlay.scaleY
      ctx.strokeStyle = "#fb7185"
      ctx.lineWidth = 1.3
      if (ctx.setLineDash)
        ctx.setLineDash([4, 3])
      ctx.beginPath()
      ctx.arc(px, py, overlay.toolCircleRadius, 0, Math.PI * 2)
      ctx.stroke()
    }
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
  }

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
    implicitWidth: toolLabel.implicitWidth + 20
    implicitHeight: toolLabel.implicitHeight + 16

    Label {
      id: toolLabel
      anchors.centerIn: parent
      font.family: "monospace"
      color: Cores.CoreStyle.text
      horizontalAlignment: Text.AlignLeft
      verticalAlignment: Text.AlignVCenter
      text: overlay.toolVisible
            ? qsTr("机床: X=%1 Y=%2 Z=%3 RPM=%4\n像素: X=%5 Y=%6  直径=%7 mm")
                .arg(_formatNumber(toolWorldPosition.x, 3))
                .arg(_formatNumber(toolWorldPosition.y, 3))
                .arg(_formatNumber(toolWorldPosition.z, 3))
                .arg(_formatNumber(toolWorldPosition.rpm, 0))
                .arg(_formatNumber(overlay.toolPixelX, 1))
                .arg(_formatNumber(overlay.toolPixelY, 1))
                .arg(_formatNumber(toolDiameterMm, 2))
            : ""
    }
  }
}
