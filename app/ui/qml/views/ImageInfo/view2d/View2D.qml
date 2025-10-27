import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../../Api" as Api
import "../../../cores" as Cores
import "." as Layers

/* 二维图像视图
 * 展示加工区实时画面，并叠加夹具、刀具与坐标提示信息。
 */
Item {
  id: view
  Layout.fillWidth: true
  Layout.fillHeight: true

  property real imageWidth: 640
  property real imageHeight: 360
  property real pixelSizeMm: 0.2
  property var pathPoints: []
  property var toolWorldPosition: ({})
  property int fixtureColumns: 4
  property int fixtureRows: 4
  property real fixtureSizeMm: 8
  property real fixtureMarginMm: 6
  property var fixtures: []
  property var calibrationCore: null

  readonly property real scaleX: overlayArea.width > 0 ? overlayArea.width / imageWidth : 1
  readonly property real scaleY: overlayArea.height > 0 ? overlayArea.height / imageHeight : 1

  property point hoverPixel: Qt.point(-1, -1)
  property point hoverWorld: Qt.point(0, 0)
  property bool hoverValid: false

  function worldToPixel(worldPoint) {
    if (!worldPoint || worldPoint.x === undefined || worldPoint.y === undefined)
      return Qt.point(-1, -1)
    if (calibrationCore && calibrationCore.worldToImage !== undefined) {
      var mapped = calibrationCore.worldToImage(worldPoint)
      return Qt.point(mapped.x, mapped.y)
    }
    if (pixelSizeMm <= 0)
      return Qt.point(-1, -1)
    return Qt.point(worldPoint.x / pixelSizeMm, worldPoint.y / pixelSizeMm)
  }

  function resetHover() {
    hoverPixel = Qt.point(-1, -1)
    hoverWorld = Qt.point(0, 0)
    hoverValid = false
    coordinateLayer.requestUpdate()
  }

  function updateHover(localX, localY) {
    if (scaleX <= 0 || scaleY <= 0) {
      resetHover()
      return
    }
    var px = localX / scaleX
    var py = localY / scaleY
    if (px < 0 || py < 0 || px > imageWidth || py > imageHeight) {
      resetHover()
      return
    }
    hoverPixel = Qt.point(px, py)
    var worldPoint
    if (calibrationCore && calibrationCore.imageToWorld !== undefined)
      worldPoint = calibrationCore.imageToWorld({ x: px, y: py })
    else
      worldPoint = { x: px * pixelSizeMm, y: py * pixelSizeMm }
    hoverWorld = Qt.point(worldPoint.x, worldPoint.y)
    hoverValid = true
    coordinateLayer.requestUpdate()
  }

  Rectangle {
    anchors.fill: parent
    radius: 4
    color: Cores.CoreStyle.background
  }

  Image {
    id: img
    anchors.fill: parent
    asynchronous: true
    cache: false
    smooth: true
    fillMode: Image.PreserveAspectFit
    source: Cores.CoreState.current2dImageSource
  Item {
    id: overlayArea
    width: img.paintedWidth
    height: img.paintedHeight
    anchors.centerIn: parent
    visible: img.status === Image.Ready && width > 0 && height > 0
    clip: true

    Canvas {
      id: pathCanvas
      anchors.fill: parent
      onPaint: {
        var ctx = getContext("2d")
        ctx.clearRect(0, 0, width, height)

        var centerX = width / 2
        var centerY = height / 2
        var lenX = 16 * view.scaleX
        var lenY = 16 * view.scaleY

        ctx.strokeStyle = "#22d3ee"
        ctx.lineWidth = 1.2
        ctx.beginPath()
        ctx.moveTo(centerX - lenX, centerY)
        ctx.lineTo(centerX + lenX, centerY)
        ctx.moveTo(centerX, centerY - lenY)
        ctx.lineTo(centerX, centerY + lenY)
        ctx.stroke()

        var pts = view.pathPoints || []
        if (!pts || pts.length < 2)
          return

        ctx.strokeStyle = "#10b981"
        ctx.lineWidth = 2
        ctx.beginPath()
        for (var i = 0; i < pts.length; ++i) {
          var px = pts[i].x * view.scaleX
          var py = pts[i].y * view.scaleY
          if (i === 0)
            ctx.moveTo(px, py)
          else
            ctx.lineTo(px, py)
        }
        ctx.stroke()

        var startX = pts[0].x * view.scaleX
        var startY = pts[0].y * view.scaleY
        var endX = pts[pts.length - 1].x * view.scaleX
        var endY = pts[pts.length - 1].y * view.scaleY

        ctx.fillStyle = "#f59e0b"
        ctx.beginPath()
        ctx.arc(startX, startY, 4, 0, Math.PI * 2)
        ctx.fill()

        ctx.fillStyle = "#ef4444"
        ctx.beginPath()
        ctx.arc(endX, endY, 4, 0, Math.PI * 2)
        ctx.fill()
      }
      onWidthChanged: requestPaint()
      onHeightChanged: requestPaint()
      Component.onCompleted: requestPaint()
    }

    Layers.FixtureOverlay {
      anchors.fill: parent
      columns: view.fixtureColumns
      rows: view.fixtureRows
      imageWidth: view.imageWidth
      imageHeight: view.imageHeight
      pixelSizeMm: view.pixelSizeMm
      fixtureSizeMm: view.fixtureSizeMm
      fixtureMarginMm: view.fixtureMarginMm
      scaleX: view.scaleX
      scaleY: view.scaleY
      fixtures: view.fixtures
    }

    Layers.ToolOverlay {
      anchors.fill: parent
      toolWorldPosition: view.toolWorldPosition
      pixelSizeMm: view.pixelSizeMm
      imageWidth: view.imageWidth
      imageHeight: view.imageHeight
      scaleX: view.scaleX
      scaleY: view.scaleY
    }

    Layers.CoordinateOverlay {
      id: coordinateLayer
      anchors.fill: parent
      hoverPixel: view.hoverPixel
      hoverWorld: view.hoverWorld
      hoverValid: view.hoverValid
      scaleX: view.scaleX
      scaleY: view.scaleY
    }

    MouseArea {
      anchors.fill: parent
      hoverEnabled: true
      acceptedButtons: Qt.NoButton
      onPositionChanged: view.updateHover(mouse.x, mouse.y)
      onExited: view.resetHover()
    }
  }

  onPathPointsChanged: pathCanvas.requestPaint()
  onScaleXChanged: {
    pathCanvas.requestPaint()
    coordinateLayer.requestUpdate()
  }
  onScaleYChanged: {
    pathCanvas.requestPaint()
    coordinateLayer.requestUpdate()
  }

  Connections {
    target: img
    function onPaintedWidthChanged() { pathCanvas.requestPaint() }
    function onPaintedHeightChanged() { pathCanvas.requestPaint() }
  }

  Connections {
    target: overlayArea
    function onWidthChanged() { pathCanvas.requestPaint() }
    function onHeightChanged() { pathCanvas.requestPaint() }
  }
}
