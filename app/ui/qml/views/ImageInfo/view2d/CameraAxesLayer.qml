import QtQuick
import "../../../cores" as Cores

Item {
  id: layer
  anchors.fill: parent

  property bool enabled: true
  property real axisLengthMm: 40
  property color axisColorX: "#ef4444"
  property color axisColorY: "#22c55e"
  property var calibrationCore: Cores.CoreDataView
  property var viewItem
  property real scaleX: 1.0
  property real scaleY: 1.0
  property int recordId: -1
  property point originPixel: Qt.point(-1, -1)
  property point xAxisPixel: Qt.point(-1, -1)
  property point yAxisPixel: Qt.point(-1, -1)
  property int _updateToken: 0

  function _resetPixels() {
    originPixel = Qt.point(-1, -1)
    xAxisPixel = Qt.point(-1, -1)
    yAxisPixel = Qt.point(-1, -1)
  }

  function requestUpdate() {
    layer._updateToken += 1
    var token = layer._updateToken

    if (!layer.enabled) {
      _resetPixels()
      axesCanvas.requestPaint()
      return
    }

    var core = layer.calibrationCore || Cores.CoreDataView
    if (!core || typeof core.cameraToPixel !== "function") {
      _resetPixels()
      axesCanvas.requestPaint()
      return
    }

    var lookupOptions = {}
    if (layer.recordId !== undefined && layer.recordId !== null && layer.recordId > 0)
      lookupOptions.recordId = layer.recordId

    var originPromise = core.cameraToPixel({ x: 0, y: 0, z: 0 }, lookupOptions)
    var xPromise = core.cameraToPixel({ x: layer.axisLengthMm, y: 0, z: 0 }, lookupOptions)
    var yPromise = core.cameraToPixel({ x: 0, y: layer.axisLengthMm, z: 0 }, lookupOptions)

    Promise.all([originPromise, xPromise, yPromise]).then(function(results) {
      if (layer._updateToken !== token)
        return
      originPixel = results[0]
      xAxisPixel = results[1]
      yAxisPixel = results[2]
      axesCanvas.requestPaint()
    }).catch(function() {
      if (layer._updateToken !== token)
        return
      _resetPixels()
      axesCanvas.requestPaint()
    })
  }

  onEnabledChanged: requestUpdate()
  onAxisLengthMmChanged: requestUpdate()
  onViewItemChanged: requestUpdate()
  onCalibrationCoreChanged: requestUpdate()
  onRecordIdChanged: requestUpdate()
  onScaleXChanged: {
    if (originPixel.x >= 0 && originPixel.y >= 0)
      axesCanvas.requestPaint()
    else
      requestUpdate()
  }
  onScaleYChanged: {
    if (originPixel.x >= 0 && originPixel.y >= 0)
      axesCanvas.requestPaint()
    else
      requestUpdate()
  }

  Component.onCompleted: requestUpdate()

  Canvas {
    id: axesCanvas
    anchors.fill: parent
    visible: layer.enabled
    opacity: layer.enabled ? 1 : 0
    onPaint: {
      var ctx = getContext("2d")
      ctx.clearRect(0, 0, width, height)
      if (!layer.enabled)
        return
      if (!(layer.scaleX > 0 && layer.scaleY > 0))
        return
      var origin = layer.originPixel
      if (!origin || origin.x < 0 || origin.y < 0)
        return

      var originDisplay = Qt.point(origin.x * layer.scaleX, origin.y * layer.scaleY)

      ctx.save()
      ctx.lineWidth = 2
      ctx.lineCap = "round"
      ctx.fillStyle = "#38bdf8"
      ctx.beginPath()
      ctx.arc(originDisplay.x, originDisplay.y, 4, 0, Math.PI * 2)
      ctx.fill()

      function drawAxis(endpointPixel, color, label) {
        if (!endpointPixel || endpointPixel.x < 0 || endpointPixel.y < 0)
          return
        var endpoint = Qt.point(endpointPixel.x * layer.scaleX, endpointPixel.y * layer.scaleY)
        if (!isFinite(endpoint.x) || !isFinite(endpoint.y))
          return
        var dx = endpoint.x - originDisplay.x
        var dy = endpoint.y - originDisplay.y
        var length = Math.hypot(dx, dy)
        if (length < 1)
          return

        ctx.save()
        ctx.strokeStyle = color
        ctx.beginPath()
        ctx.moveTo(originDisplay.x, originDisplay.y)
        ctx.lineTo(endpoint.x, endpoint.y)
        ctx.stroke()

        var headSize = 10
        var angle = Math.atan2(dy, dx)
        ctx.beginPath()
        ctx.moveTo(endpoint.x, endpoint.y)
        ctx.lineTo(endpoint.x - headSize * Math.cos(angle - Math.PI / 6),
                   endpoint.y - headSize * Math.sin(angle - Math.PI / 6))
        ctx.moveTo(endpoint.x, endpoint.y)
        ctx.lineTo(endpoint.x - headSize * Math.cos(angle + Math.PI / 6),
                   endpoint.y - headSize * Math.sin(angle + Math.PI / 6))
        ctx.stroke()

        ctx.fillStyle = color
        ctx.font = "bold 12px sans-serif"
        ctx.textAlign = "center"
        ctx.textBaseline = "middle"
        var labelOffset = 12
        ctx.fillText(label,
                     endpoint.x + labelOffset * Math.cos(angle),
                     endpoint.y + labelOffset * Math.sin(angle))
        ctx.restore()
      }

      drawAxis(layer.xAxisPixel, layer.axisColorX, "X")
      drawAxis(layer.yAxisPixel, layer.axisColorY, "Y")
      ctx.restore()
    }
  }

  Connections {
    target: calibrationCore
    ignoreUnknownSignals: true
    function onOriginXChanged() { layer.requestUpdate() }
    function onOriginYChanged() { layer.requestUpdate() }
    function onWorldWidthChanged() { layer.requestUpdate() }
    function onWorldHeightChanged() { layer.requestUpdate() }
    function onMachineMatrixChanged() {
      layer._resetPixels()
      layer.requestUpdate()
    }
    function onCameraMatrixChanged() {
      layer._resetPixels()
      layer.requestUpdate()
    }
  }
}
