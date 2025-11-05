import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../../Api" as Api
import "../../../cores" as Cores
import "../../../datas" as Datas
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
  property var calibrationCore: Cores.CoreDataView

  readonly property real fitScale: {
    if (imageWidth <= 0 || imageHeight <= 0 || width <= 0 || height <= 0)
      return 1
    var scaleW = width / imageWidth
    var scaleH = height / imageHeight
    var result = Math.min(scaleW, scaleH)
    return result > 0 ? result : 1
  }
  readonly property real displayWidth: imageWidth > 0 ? imageWidth * fitScale : 0
  readonly property real displayHeight: imageHeight > 0 ? imageHeight * fitScale : 0
  readonly property real scaleX: fitScale
  readonly property real scaleY: fitScale

  property real zoom: 1.0
  property real minZoom: 0.5
  property real maxZoom: 4.0
  property point panOffset: Qt.point(0, 0)
  property point _dragLastPos: Qt.point(0, 0)
  property real _pinchStartZoom: 1.0
  property point _pinchStartPan: Qt.point(0, 0)

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
    var invalidPixel = Qt.point(-1, -1)
    hoverPixel = invalidPixel
    hoverWorld = Qt.point(0, 0)
    hoverValid = false
    Cores.CoreDataView.clearCursor()
    coordinateLayer.requestUpdate()
  }

  function updateHover(localX, localY) {
    Cores.CoreDataView.viewPixel = Qt.point(localX, localY)
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
    var pixelPoint = Qt.point(px, py)
    hoverPixel = pixelPoint
    var worldPoint
    if (calibrationCore && calibrationCore.imageToWorld !== undefined)
      worldPoint = calibrationCore.imageToWorld({ x: px, y: py })
    else
      worldPoint = { x: px * pixelSizeMm, y: py * pixelSizeMm }
    var worldPointQt = Qt.point(worldPoint.x, worldPoint.y)
    hoverWorld = worldPointQt
    hoverValid = true
    Cores.CoreDataView.setCursor(pixelPoint, worldPointQt, true)
    coordinateLayer.requestUpdate()
  }

  function _clampZoom(value) {
    var candidate = value
    if (!isFinite(candidate) || candidate <= 0)
      candidate = 1
    return Math.min(maxZoom, Math.max(minZoom, candidate))
  }

  function _contentHalfWidth() {
    if (displayWidth <= 0 || zoom <= 0)
      return 0
    return displayWidth * zoom / 2
  }

  function _contentHalfHeight() {
    if (displayHeight <= 0 || zoom <= 0)
      return 0
    return displayHeight * zoom / 2
  }

  function _clampPan(point) {
    if (width <= 0 || height <= 0)
      return Qt.point(0, 0)
    var maxX = Math.max(0, _contentHalfWidth() - width / 2)
    var maxY = Math.max(0, _contentHalfHeight() - height / 2)
    var clampedX = Math.max(-maxX, Math.min(maxX, point.x))
    var clampedY = Math.max(-maxY, Math.min(maxY, point.y))
    return Qt.point(clampedX, clampedY)
  }

  function _updatePan(point) {
    var clamped = _clampPan(point)
    if (clamped.x !== panOffset.x || clamped.y !== panOffset.y) {
      panOffset = clamped
      if (typeof coordinateLayer !== "undefined")
        coordinateLayer.requestUpdate()
      if (typeof pathCanvas !== "undefined")
        pathCanvas.requestPaint()
      _refreshHover()
    }
  }

  function _applyPanDelta(dx, dy) {
    if (zoom <= 1.0) {
      if (panOffset.x !== 0 || panOffset.y !== 0)
        _updatePan(Qt.point(0, 0))
      return
    }
    _updatePan(Qt.point(panOffset.x + dx, panOffset.y + dy))
  }

  function _setZoom(targetZoom, focusPoint) {
    var clamped = _clampZoom(targetZoom)
    if (Math.abs(clamped - zoom) < 0.0001)
      return
    var focus = focusPoint || Qt.point(displayWidth / 2, displayHeight / 2)
    var offsetX = focus.x - displayWidth / 2
    var offsetY = focus.y - displayHeight / 2
    var deltaZoom = zoom - clamped
    zoom = clamped
    _updatePan(Qt.point(panOffset.x + offsetX * deltaZoom, panOffset.y + offsetY * deltaZoom))
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
    if (typeof coordinateLayer !== "undefined")
      coordinateLayer.requestUpdate()
    _refreshHover()
  }

  function handleWheelZoom(wheel) {
    if (typeof contentGroup === "undefined")
      return
    var delta = wheel.angleDelta.y !== 0 ? wheel.angleDelta.y / 120 : wheel.pixelDelta.y / 120
    if (delta === 0)
      return
    var factor = Math.pow(1.2, delta)
    if (Math.abs(factor - 1) < 0.0001)
      return
    var localPoint = Qt.point(wheel.x, wheel.y)
    var mappedPoint = contentGroup.mapFromItem(overlayArea, localPoint)
    _setZoom(zoom * factor, mappedPoint)
    wheel.accepted = true
  }

  function _refreshHover() {
    if (typeof interactionArea === "undefined" || typeof contentGroup === "undefined")
      return
    if (!interactionArea.containsMouse)
      return
    var pointer = Qt.point(interactionArea.mouseX, interactionArea.mouseY)
    var mapped = contentGroup.mapFromItem(overlayArea, pointer)
    updateHover(mapped.x, mapped.y)
  }

  Rectangle {
    anchors.fill: parent
    radius: 4
    color: Cores.CoreStyle.background
  }

  Item {
    id: viewport
    anchors.fill: parent

    Item {
      id: overlayArea
      width: view.displayWidth
      height: view.displayHeight
      anchors.centerIn: parent
      visible: captureImage.status === Image.Ready && width > 0 && height > 0
      clip: true

      Item {
        id: contentGroup
        width: overlayArea.width
        height: overlayArea.height
        anchors.centerIn: parent
        transform: [
          Scale {
            origin.x: overlayArea.width / 2
            origin.y: overlayArea.height / 2
            xScale: view.zoom
            yScale: view.zoom
          },
          Translate {
            x: view.panOffset.x
            y: view.panOffset.y
          }
        ]

        Layers.ImageLayer {
          id: captureImage
          anchors.fill: parent
          fillMode: Image.Stretch
          source: Cores.CoreState.current2dImageSource
          onPaintedSizeUpdated: {
            if (sourceSize && sourceSize.width > 0 && sourceSize.height > 0) {
              view.imageWidth = sourceSize.width
              view.imageHeight = sourceSize.height
              Datas.CalibrationData.imageWidth = sourceSize.width
              Datas.CalibrationData.imageHeight = sourceSize.height
            }
            view._updatePan(view.panOffset)
            pathCanvas.requestPaint()
            coordinateLayer.requestUpdate()
          }
        }
        Layers.MaskLayer {
          id: particleMaskImage
          anchors.fill: parent
          fillMode: Image.Stretch
          source: Cores.CoreState.particleMaskSource
          maskOpacity: 0.7
          visibleMask: Cores.CoreState.showParticleMask
        }
        Canvas {
          id: pathCanvas
          anchors.fill: parent
          visible: Cores.CoreState.showPathOverlay
          onPaint: {
            if (!Cores.CoreState.showPathOverlay)
              return
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

            var strokeColor = Cores.CoreCutting.runState === "RUNNING"
                              ? Cores.CoreStyle.accent
                              : Cores.CoreStyle.info
            ctx.strokeStyle = strokeColor
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

            ctx.fillStyle = strokeColor
            ctx.beginPath()
            ctx.arc(startX, startY, 4, 0, Math.PI * 2)
            ctx.fill()

            ctx.fillStyle = Cores.CoreStyle.danger
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
          scaleX: view.scaleX
          scaleY: view.scaleY
          showLabel: false
        }
      }

      PinchHandler {
        id: pinchHandler
        target: null
        onActiveChanged: {
          if (active) {
            minimumScale = view.minZoom / view.zoom
            maximumScale = view.maxZoom / view.zoom
            view._pinchStartZoom = view.zoom
            view._pinchStartPan = view.panOffset
          } else {
            view._refreshHover()
          }
        }
        onScaleChanged: {
          var desired = view._pinchStartZoom * scale
          var focus = contentGroup.mapFromItem(overlayArea, centroid.position)
          view._setZoom(desired, focus)
        }
        onTranslationChanged: {
          var newPan = Qt.point(view._pinchStartPan.x + translation.x, view._pinchStartPan.y + translation.y)
          view._updatePan(newPan)
        }
      }

      MouseArea {
        id: interactionArea
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton
        cursorShape: pressed ? Qt.ClosedHandCursor : (view.zoom > 1.0001 ? Qt.OpenHandCursor : Qt.ArrowCursor)

        onPressed: function(mouse) {
          view._dragLastPos = Qt.point(mouse.x, mouse.y)
        }

        onPositionChanged: function(mouse) {
          var localPoint = Qt.point(mouse.x, mouse.y)
          if (pressed) {
            var dx = mouse.x - view._dragLastPos.x
            var dy = mouse.y - view._dragLastPos.y
            view._applyPanDelta(dx, dy)
            view._dragLastPos = localPoint
          }
          var mapped = contentGroup.mapFromItem(overlayArea, localPoint)
          view.updateHover(mapped.x, mapped.y)
        }

        onReleased: view._refreshHover()
        onCanceled: view._refreshHover()
        onExited: view.resetHover()

        onWheel: function(wheel) {
          handleWheelZoom(wheel)
        }
      }

      onWidthChanged: Cores.CoreDataView.viewWidth = width
      onHeightChanged: Cores.CoreDataView.viewHeight = height
    }
  }

  Layers.CoordinateInfo {
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.margins: 12
  }

  onPathPointsChanged: {
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
  }
  onScaleXChanged: {
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
    if (typeof coordinateLayer !== "undefined")
      coordinateLayer.requestUpdate()
  }
  onScaleYChanged: {
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
    if (typeof coordinateLayer !== "undefined")
      coordinateLayer.requestUpdate()
  }

  onZoomChanged: {
    _updatePan(panOffset)
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
    if (typeof coordinateLayer !== "undefined")
      coordinateLayer.requestUpdate()
  }

  onPanOffsetChanged: {
    if (typeof coordinateLayer !== "undefined")
      coordinateLayer.requestUpdate()
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
    _refreshHover()
  }
  onWidthChanged: _updatePan(panOffset)
  onHeightChanged: _updatePan(panOffset)
  onDisplayWidthChanged: _updatePan(panOffset)
  onDisplayHeightChanged: _updatePan(panOffset)

  Connections {
    target: overlayArea
    function onWidthChanged() {
      if (typeof pathCanvas !== "undefined")
        pathCanvas.requestPaint()
    }
    function onHeightChanged() {
      if (typeof pathCanvas !== "undefined")
        pathCanvas.requestPaint()
    }
  }

  Connections {
    target: Cores.CoreState
    function onShowPathOverlayChanged() {
      if (typeof pathCanvas !== "undefined")
        pathCanvas.requestPaint()
    }
    function onParticleMaskSourceChanged() { /* trigger overlay updates via binding */ }
  }
}
