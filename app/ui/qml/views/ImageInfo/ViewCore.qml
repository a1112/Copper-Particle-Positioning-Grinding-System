
pragma Singleton
import QtQuick

QtObject {
  id: core

  // Shared interactive state --------------------------------------------------
  property real zoom: 1.0
  property real minZoom: 0.5
  property real maxZoom: 4.0
  property point panOffset: Qt.point(0, 0)
  property point dragLastPos: Qt.point(0, 0)
  property real pinchStartZoom: 1.0
  property point pinchStartPan: Qt.point(0, 0)

  property point hoverPixel: Qt.point(-1, -1)
  property point hoverWorld: Qt.point(0, 0)
  property bool hoverValid: false

  property bool showCameraAxes: true

  property bool simulateActive: false
  property int simulateIndex: -1
  property int simulateIntervalMs: 80

  // Helper methods -----------------------------------------------------------

  function clampZoom(value) {
    var candidate = (isFinite(value) && value > 0) ? value : 1
    if (candidate < minZoom)
      return minZoom
    if (candidate > maxZoom)
      return maxZoom
    return candidate
  }

  function contentHalfWidth(displayWidth) {
    if (displayWidth <= 0 || zoom <= 0)
      return 0
    return displayWidth * zoom / 2
  }

  function contentHalfHeight(displayHeight) {
    if (displayHeight <= 0 || zoom <= 0)
      return 0
    return displayHeight * zoom / 2
  }

  function clampPan(point, ctx) {
    if (!ctx || ctx.width <= 0 || ctx.height <= 0)
      return Qt.point(0, 0)
    var maxX = Math.max(0, contentHalfWidth(ctx.displayWidth) - ctx.width / 2)
    var maxY = Math.max(0, contentHalfHeight(ctx.displayHeight) - ctx.height / 2)
    return Qt.point(
      Math.max(-maxX, Math.min(maxX, point.x)),
      Math.max(-maxY, Math.min(maxY, point.y))
    )
  }

  function updatePan(point, ctx) {
    var clamped = clampPan(point, ctx)
    if (panOffset.x === clamped.x && panOffset.y === clamped.y)
      return panOffset
    panOffset = clamped
    if (ctx && ctx.coordinateLayer && ctx.coordinateLayer.requestUpdate)
      ctx.coordinateLayer.requestUpdate()
    if (ctx && ctx.pathCanvas && ctx.pathCanvas.requestPaint)
      ctx.pathCanvas.requestPaint()
    if (ctx && ctx.refreshHover)
      ctx.refreshHover()
    return panOffset
  }

  function applyPanDelta(dx, dy, ctx) {
    if (zoom <= 1.0) {
      if (panOffset.x !== 0 || panOffset.y !== 0)
        updatePan(Qt.point(0, 0), ctx)
      return
    }
    updatePan(Qt.point(panOffset.x + dx, panOffset.y + dy), ctx)
  }

  function setZoom(targetZoom, focusPoint, ctx) {
    if (!ctx)
      return
    var clamped = clampZoom(targetZoom)
    if (Math.abs(clamped - zoom) < 0.0001)
      return
    var focus = focusPoint || Qt.point(ctx.displayWidth / 2, ctx.displayHeight / 2)
    var offsetX = focus.x - ctx.displayWidth / 2
    var offsetY = focus.y - ctx.displayHeight / 2
    var deltaZoom = zoom - clamped
    zoom = clamped
    updatePan(Qt.point(panOffset.x + offsetX * deltaZoom, panOffset.y + offsetY * deltaZoom), ctx)
    if (ctx.pathCanvas && ctx.pathCanvas.requestPaint)
      ctx.pathCanvas.requestPaint()
    if (ctx.coordinateLayer && ctx.coordinateLayer.requestUpdate)
      ctx.coordinateLayer.requestUpdate()
    if (ctx.refreshHover)
      ctx.refreshHover()
  }

  function resetHover(ctx) {
    hoverPixel = Qt.point(-1, -1)
    hoverWorld = Qt.point(0, 0)
    hoverValid = false
    if (ctx && ctx.coordinateLayer && ctx.coordinateLayer.requestUpdate)
      ctx.coordinateLayer.requestUpdate()
    if (ctx && ctx.clearCursor)
      ctx.clearCursor()
  }

  function updateHover(localX, localY, ctx) {
    if (!ctx) {
      resetHover(null)
      return
    }
    if (ctx.scaleX <= 0 || ctx.scaleY <= 0) {
      resetHover(ctx)
      return
    }
    var px = localX / ctx.scaleX
    var py = localY / ctx.scaleY
    if (px < 0 || py < 0 || px > ctx.imageWidth || py > ctx.imageHeight) {
      resetHover(ctx)
      return
    }
    var worldPoint
    if (ctx.calibrationCore && ctx.calibrationCore.imageToWorld !== undefined)
      worldPoint = ctx.calibrationCore.imageToWorld({ x: px, y: py })
    else
      worldPoint = { x: px * ctx.pixelSizeMm, y: py * ctx.pixelSizeMm }
    hoverPixel = Qt.point(px, py)
    hoverWorld = Qt.point(worldPoint.x, worldPoint.y)
    hoverValid = true
    if (ctx.coordinateLayer && ctx.coordinateLayer.requestUpdate)
      ctx.coordinateLayer.requestUpdate()
    if (ctx.onHoverChanged)
      ctx.onHoverChanged(hoverPixel, hoverWorld)
  }

  function refreshHover(ctx) {
    if (!hoverValid || !ctx)
      return
    var localX = hoverPixel.x * ctx.scaleX
    var localY = hoverPixel.y * ctx.scaleY
    if (localX < 0 || localY < 0 || localX > ctx.overlayWidth || localY > ctx.overlayHeight) {
      resetHover(ctx)
      return
    }
    if (ctx.updateHover)
      ctx.updateHover(localX, localY)
  }

  // Simulation helpers -------------------------------------------------------

  function _normalizePath(pathPoints) {
    if (!Array.isArray(pathPoints))
      return []
    return pathPoints
  }

  function startSimulation(pathPoints) {
    var pts = _normalizePath(pathPoints)
    if (!pts.length) {
      simulateActive = false
      simulateIndex = -1
      return false
    }
    simulateIndex = 0
    simulateActive = true
    return true
  }

  function stopSimulation() {
    var changed = simulateActive || simulateIndex >= 0
    simulateActive = false
    simulateIndex = -1
    return changed
  }

  function toggleSimulation(pathPoints) {
    if (simulateActive) {
      stopSimulation()
      return false
    }
    return startSimulation(pathPoints)
  }

  function stepSimulation(pathPoints) {
    if (!simulateActive) {
      simulateIndex = -1
      return false
    }
    var pts = _normalizePath(pathPoints)
    var count = pts.length
    if (!count) {
      stopSimulation()
      return false
    }
    var next = simulateIndex
    if (next < 0 || next >= count - 1)
      next = 0
    else
      next += 1
    simulateIndex = next
    return true
  }
}
