import QtQuick
import QtQuick.Controls

Item {
  id: overlay
  anchors.fill: parent

  property var singleRects: []
  property var areaRects: []
  property real scaleX: 1.0
  property real scaleY: 1.0
  property color areaFillColor: Qt.rgba(0.95, 0.64, 0.13, 0.18)
  property color areaBorderColor: Qt.rgba(0.98, 0.57, 0.09, 0.8)
  property color singleFillColor: Qt.rgba(0.9, 0.25, 0.35, 0.25)
  property color singleBorderColor: Qt.rgba(0.86, 0.12, 0.28, 0.95)

  readonly property int _areaCount: areaRects && areaRects.length ? areaRects.length : 0
  readonly property int _singleCount: singleRects && singleRects.length ? singleRects.length : 0

  visible: _areaCount > 0 || _singleCount > 0

  readonly property var _x1Keys: ["X1", "x1", "xmin", "xMin", "left", "col", "col1"]
  readonly property var _x2Keys: ["X2", "x2", "xmax", "xMax", "right", "col2"]
  readonly property var _y1Keys: ["Y1", "y1", "ymin", "yMin", "top", "row", "row1"]
  readonly property var _y2Keys: ["Y2", "y2", "ymax", "yMax", "bottom", "row2"]

  function _pickNumber(source, keys) {
    if (!source)
      return NaN
    for (var i = 0; i < keys.length; ++i) {
      var key = keys[i]
      if (source[key] !== undefined && source[key] !== null) {
        var num = Number(source[key])
        if (!isNaN(num))
          return num
      }
    }
    return NaN
  }

  function _rectMetrics(entry) {
    if (!entry)
      return null
    var x1 = _pickNumber(entry, _x1Keys)
    var x2 = _pickNumber(entry, _x2Keys)
    var y1 = _pickNumber(entry, _y1Keys)
    var y2 = _pickNumber(entry, _y2Keys)
    if (!isFinite(x1) || !isFinite(x2) || !isFinite(y1) || !isFinite(y2))
      return null
    var left = Math.min(x1, x2)
    var right = Math.max(x1, x2)
    var top = Math.min(y1, y2)
    var bottom = Math.max(y1, y2)
    var width = Math.max(0, right - left)
    var height = Math.max(0, bottom - top)
    if (width <= 0 || height <= 0)
      return null
    return {
      x: left,
      y: top,
      width: width,
      height: height
    }
  }

  Repeater {
    model: overlay._areaCount
    delegate: Rectangle {
      readonly property var metrics: overlay._rectMetrics(overlay.areaRects[index])
      visible: metrics !== null
      x: metrics ? metrics.x * overlay.scaleX : 0
      y: metrics ? metrics.y * overlay.scaleY : 0
      width: metrics ? Math.max(1, metrics.width * overlay.scaleX) : 0
      height: metrics ? Math.max(1, metrics.height * overlay.scaleY) : 0
      color: overlay.areaFillColor
      border.color: overlay.areaBorderColor
      border.width: 1
      radius: 2
    }
  }

  Repeater {
    model: overlay._singleCount
    delegate: Rectangle {
      readonly property var metrics: overlay._rectMetrics(overlay.singleRects[index])
      visible: metrics !== null
      x: metrics ? metrics.x * overlay.scaleX : 0
      y: metrics ? metrics.y * overlay.scaleY : 0
      width: metrics ? Math.max(1, metrics.width * overlay.scaleX) : 0
      height: metrics ? Math.max(1, metrics.height * overlay.scaleY) : 0
      color: overlay.singleFillColor
      border.color: overlay.singleBorderColor
      border.width: 1
      radius: 1
    }
  }
}
