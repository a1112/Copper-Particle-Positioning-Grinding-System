import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../../Api" as Api
import "../../../cores" as Cores
import "../../../datas" as Datas
import "." as Layers
import ".." as ImageInfo

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
  property var defectAreaRects: []
  property var defectSingleRects: []
  property var calibrationCore: Cores.CoreDataView
  property int recordId: Datas.TaskDatas.latestRecordId
  property var viewCore: ImageInfo.ViewCore{}


  readonly property real currentZoom: viewCore ? viewCore.zoom : 1.0
  readonly property point currentPanOffset: viewCore ? viewCore.panOffset : Qt.point(0, 0)
  readonly property bool simulateActive: viewCore ? viewCore.simulateActive : false
  readonly property int currentSimulateIndex: viewCore ? viewCore.simulateIndex : -1

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

  function resetHover() {
    if (!viewCore)
      return
    viewCore.resetHover({
                          coordinateLayer: coordinateLayer,
                          clearCursor: function() { Cores.CoreDataView.clearCursor() }
                        })
  }

  function updateHover(localX, localY) {
    if (!viewCore)
      return
    viewCore.updateHover(localX, localY, {
                           scaleX: scaleX,
                           scaleY: scaleY,
                           imageWidth: imageWidth,
                           imageHeight: imageHeight,
                           pixelSizeMm: pixelSizeMm,
                           calibrationCore: calibrationCore,
                           coordinateLayer: coordinateLayer,
                           onHoverChanged: function(pixelPoint, worldPoint) {
                             Cores.CoreDataView.setCursor(pixelPoint, worldPoint, true)
                           }
                         })
  }

  function _corePanContext() {
    return {
      width: overlayArea ? overlayArea.width : width,
      height: overlayArea ? overlayArea.height : height,
      displayWidth: displayWidth,
      displayHeight: displayHeight,
      coordinateLayer: coordinateLayer,
      pathCanvas: pathCanvas,
      refreshHover: _refreshHover
    }
  }

  function _applyPanDelta(dx, dy) {
    if (!viewCore)
      return
    viewCore.applyPanDelta(dx, dy, _corePanContext())
  }

  function _updatePan(point) {
    if (!viewCore)
      return
    viewCore.updatePan(point, _corePanContext())
  }

  function _setZoom(targetZoom, focusPoint) {
    if (!viewCore)
      return
    viewCore.setZoom(targetZoom, focusPoint, _corePanContext())
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
    _setZoom(currentZoom * factor, mappedPoint)
    wheel.accepted = true
  }

  function _refreshHover() {
    if (typeof contentGroup === "undefined" || !viewCore || !viewCore.hoverValid)
      return
    var localX = viewCore.hoverPixel.x * scaleX
    var localY = viewCore.hoverPixel.y * scaleY
    if (!overlayArea || localX < 0 || localY < 0 || localX > overlayArea.width || localY > overlayArea.height) {
      resetHover()
      return
    }
    updateHover(localX, localY)
  }

  function startSimulation() {
    if (!viewCore)
      return
    var started = viewCore.startSimulation(pathPoints)
    if (!started)
      return
    playbackTimer.start()
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
  }

  function stopSimulation() {
    if (!viewCore)
      return
    var changed = viewCore.stopSimulation()
    if (!changed)
      return
    playbackTimer.stop()
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
  }

  function toggleSimulation() {
    if (!viewCore)
      return
    var active = viewCore.toggleSimulation(pathPoints)
    if (active)
      playbackTimer.start()
    else
      playbackTimer.stop()
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
  }

  function _stepSimulation() {
    if (!viewCore)
      return
    var progressed = viewCore.stepSimulation(pathPoints)
    if (!progressed) {
      playbackTimer.stop()
      return
    }
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
  }

  Rectangle {
    anchors.fill: parent
    radius: 4
    color: Cores.CoreStyle.background
  }

  Timer {
    id: playbackTimer
    interval: Math.max(20, view.viewCore ? view.viewCore.simulateIntervalMs : 80)
    repeat: true
    running: view.simulateActive
    onTriggered: view._stepSimulation()
  }

  Item {
    id: viewport
    anchors.fill: parent
    clip: true
    Item {
      id: overlayArea
      width: view.displayWidth
      height: view.displayHeight
      anchors.centerIn: parent

      visible: captureImage.status === Image.Ready && width > 0 && height > 0
      Item {
        id: contentGroup
        width: overlayArea.width
        height: overlayArea.height
        // 不进行居中
        transform: [
          Scale {
            origin.x: overlayArea.width / 2
            origin.y: overlayArea.height / 2
            xScale: view.currentZoom
            yScale: view.currentZoom
          },
          Translate {
            x: view.currentPanOffset.x
            y: view.currentPanOffset.y
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
            view._updatePan(view.currentPanOffset)
            pathCanvas.requestPaint()
            coordinateLayer.requestUpdate()
            if (typeof cameraAxes !== "undefined")
              cameraAxes.requestUpdate()
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
            var count = Array.isArray(pts) ? pts.length : 0

            if (count >= 2) {
              var strokeColor = Cores.CoreCutting.runState === "RUNNING"
                  ? Cores.CoreStyle.accent
                  : Cores.CoreStyle.info
              ctx.strokeStyle = strokeColor
              ctx.lineWidth = 2
              ctx.beginPath()
              for (var i = 0; i < count; ++i) {
                var px = pts[i].x * view.scaleX
                var py = pts[i].y * view.scaleY
                if (i === 0)
                  ctx.moveTo(px, py)
                else
                  ctx.lineTo(px, py)
              }
              ctx.stroke()
            }

            if (count === 0)
              return

            ctx.lineWidth = 1
            ctx.font = "10px 'Monospace'"
            ctx.textAlign = "left"
            ctx.textBaseline = "top"

            for (var p = 0; p < count; ++p) {
              var point = pts[p]
              if (!point)
                continue
              var pointX = Number(point.x || 0) * view.scaleX
              var pointY = Number(point.y || 0) * view.scaleY
              var isStart = (p === 0)
              var isEnd = (p === count - 1)
              var baseColor = isStart ? "#10b981" : (isEnd ? "#ef4444" : "#0ea5e9")
              var radius = isStart || isEnd ? 4 : 3
              ctx.beginPath()
              ctx.fillStyle = baseColor
              ctx.strokeStyle = "rgba(14,116,144,0.55)"
              ctx.arc(pointX, pointY, radius, 0, Math.PI * 2)
              ctx.fill()
              ctx.stroke()

              if (point.def !== undefined && point.def !== null && point.def !== "") {
                ctx.fillStyle = Cores.CoreStyle.text
                ctx.fillText(String(point.def), pointX + 6, pointY - 6)
              }
            }

            if (view.currentSimulateIndex >= 0 && view.currentSimulateIndex < count) {
              var simPoint = pts[view.currentSimulateIndex]
              var simX = Number(simPoint.x || 0) * view.scaleX
              var simY = Number(simPoint.y || 0) * view.scaleY
              ctx.beginPath()
              ctx.fillStyle = "#f97316"
              ctx.strokeStyle = "#fb923c"
              ctx.lineWidth = 2
              ctx.arc(simX, simY, 6, 0, Math.PI * 2)
              ctx.fill()
              ctx.stroke()
            }
          }
          onWidthChanged: requestPaint()
          onHeightChanged: requestPaint()
          Component.onCompleted: requestPaint()
        }

        Layers.DefectOverlay {
          anchors.fill: parent
          areaRects: view.defectAreaRects
          singleRects: view.defectSingleRects
          scaleX: view.scaleX
          scaleY: view.scaleY
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

        Layers.CameraAxesLayer {
          id: cameraAxes
          anchors.fill: parent
          z: -1
          enabled: view.viewCore ? view.viewCore.showCameraAxes : true
          viewItem: view
          calibrationCore: view.calibrationCore
          scaleX: view.scaleX
          scaleY: view.scaleY
          recordId: view.recordId
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
            var minValue = view.viewCore ? view.viewCore.minZoom : 0.5
            var maxValue = view.viewCore ? view.viewCore.maxZoom : 4.0
            minimumScale = minValue / view.currentZoom
            maximumScale = maxValue / view.currentZoom
            if (view.viewCore) {
              view.viewCore.pinchStartZoom = view.currentZoom
              view.viewCore.pinchStartPan = view.currentPanOffset
            }
          } else {
            view._refreshHover()
          }
        }
        onScaleChanged: {
          var baseZoom = view.viewCore ? view.viewCore.pinchStartZoom : view.currentZoom
          var desired = baseZoom * scale
          var focus = contentGroup.mapFromItem(overlayArea, centroid.position)
          view._setZoom(desired, focus)
        }
        onTranslationChanged: {
          var basePan = view.viewCore ? view.viewCore.pinchStartPan : view.currentPanOffset
          var newPan = Qt.point(basePan.x + translation.x, basePan.y + translation.y)
          view._updatePan(newPan)
        }
      }

      onWidthChanged: Cores.CoreDataView.viewWidth = width
      onHeightChanged: Cores.CoreDataView.viewHeight = height
    }

    MouseArea {
      id: interactionArea
      anchors.fill: parent
      hoverEnabled: true
      acceptedButtons: Qt.LeftButton
      cursorShape: pressed ? Qt.ClosedHandCursor : (view.currentZoom > 1.0001 ? Qt.OpenHandCursor : Qt.ArrowCursor)

      onPressed: function(mouse) {
        if (view.viewCore)
          view.viewCore.dragLastPos = Qt.point(mouse.x, mouse.y)
      }

      onPositionChanged: function(mouse) {
        var localPoint = Qt.point(mouse.x, mouse.y)
        if (pressed) {
          var lastPos = view.viewCore ? view.viewCore.dragLastPos : Qt.point(mouse.x, mouse.y)
          var dx = mouse.x - lastPos.x
          var dy = mouse.y - lastPos.y
          view._applyPanDelta(dx, dy)
          if (view.viewCore)
            view.viewCore.dragLastPos = localPoint
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

  }
  Layers.CoordinateInfo {
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.margins: 12
  }
  Button {
    id: simulateButton
    text: view.simulateActive ? qsTr("停止模拟") : qsTr("模拟路径")
    anchors.top: parent.top
    anchors.right: parent.right
    anchors.margins: 12
    visible: (view.pathPoints && view.pathPoints.length > 0)
    z: 100
    onClicked: view.toggleSimulation()
  }

  onPathPointsChanged: {
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
    var pts = pathPoints || []
    var count = Array.isArray(pts) ? pts.length : 0
    if (count === 0) {
      if (view.viewCore)
        view.viewCore.simulateIndex = -1
      if (simulateActive)
        stopSimulation()
    } else if (view.viewCore && view.viewCore.simulateIndex >= count) {
      view.viewCore.simulateIndex = count - 1
    }
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

  onWidthChanged: _updatePan(currentPanOffset)
  onHeightChanged: _updatePan(currentPanOffset)
  onDisplayWidthChanged: _updatePan(currentPanOffset)
  onDisplayHeightChanged: _updatePan(currentPanOffset)
  onCalibrationCoreChanged: {
    if (typeof cameraAxes !== "undefined")
      cameraAxes.requestUpdate()
  }
  onPixelSizeMmChanged: {
    if (typeof cameraAxes !== "undefined")
      cameraAxes.requestUpdate()
  }
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
      if (!Cores.CoreState.showPathOverlay && view.simulateActive)
        view.stopSimulation()
    }
    function onParticleMaskSourceChanged() { /* trigger overlay updates via binding */ }
  }

  Connections {
    target: viewCore
    ignoreUnknownSignals: true
    function onZoomChanged() {
      _updatePan(view.currentPanOffset)
      if (typeof pathCanvas !== "undefined")
        pathCanvas.requestPaint()
      if (typeof coordinateLayer !== "undefined")
        coordinateLayer.requestUpdate()
    }
    function onPanOffsetChanged() {
      if (typeof coordinateLayer !== "undefined")
        coordinateLayer.requestUpdate()
      if (typeof pathCanvas !== "undefined")
        pathCanvas.requestPaint()
      _refreshHover()
    }
    function onShowCameraAxesChanged() {
      if (typeof cameraAxes !== "undefined")
        cameraAxes.requestUpdate()
    }
  }

  Connections {
    target: calibrationCore
    ignoreUnknownSignals: true
    function onOriginXChanged() {
      if (typeof cameraAxes !== "undefined")
        cameraAxes.requestUpdate()
    }
    function onOriginYChanged() {
      if (typeof cameraAxes !== "undefined")
        cameraAxes.requestUpdate()
    }
    function onWorldWidthChanged() {
      if (typeof cameraAxes !== "undefined")
        cameraAxes.requestUpdate()
    }
    function onWorldHeightChanged() {
      if (typeof cameraAxes !== "undefined")
        cameraAxes.requestUpdate()
    }
    function onMachineMatrixChanged() {
      if (typeof cameraAxes !== "undefined")
        cameraAxes.requestUpdate()
    }
  }

  Connections {
    target: Datas.TaskDatas
    ignoreUnknownSignals: true
    function onLatestRecordIdChanged() {
      if (typeof cameraAxes !== "undefined")
        cameraAxes.requestUpdate()
      if (view.simulateActive)
        view.stopSimulation()
    }
  }
}
