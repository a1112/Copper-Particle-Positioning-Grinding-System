import QtQuick

Item {
  id: core3D

  // Object transform
  property real objectRotationX: 0
  property real objectRotationY: 0
  property real objectRotationZ: -90
  property vector3d objectScale: Qt.vector3d(1, 1, 1)
  property real objectOffsetX: 0
  property real objectOffsetY: 0
  property real objectOffsetZ: 0

  // Camera transform
  property real cameraOffsetX: 0
  property real cameraOffsetY: 0
  property real cameraOffsetZ: 600

  // Internal state for gesture handling
  property real _startX: 0
  property real _startY: 0
  property real _startRotationX: 0
  property real _startRotationY: 0
  property real _startPanX: 0
  property real _startPanY: 0

  function beginRotate(x, y) {
    _startX = x
    _startY = y
    _startRotationX = objectRotationX
    _startRotationY = objectRotationY
  }

  function rotateTo(x, y) {
    var dx = x - _startX
    var dy = y - _startY
    objectRotationX = _startRotationX - dy * 0.5
    objectRotationY = _startRotationY + dx * 0.5
  }

  function beginPan(x, y) {
    _startX = x
    _startY = y
    _startPanX = cameraOffsetX
    _startPanY = cameraOffsetY
  }

  function panTo(x, y) {
    var dx = x - _startX
    var dy = y - _startY
    cameraOffsetX = _startPanX - dx
    cameraOffsetY = _startPanY + dy
  }

  function adjustZoom(delta) {
    var newZ = cameraOffsetZ - delta * 0.5
    cameraOffsetZ = Math.max(60, Math.min(newZ, 20000))
  }

  function resetView() {
    objectRotationX = 0
    objectRotationY = 0
    objectRotationZ = -90
    objectScale = Qt.vector3d(1, 1, 1)
    objectOffsetX = 0
    objectOffsetY = 0
    objectOffsetZ = 0
    cameraOffsetX = 0
    cameraOffsetY = 0
    cameraOffsetZ = 600
  }
}
