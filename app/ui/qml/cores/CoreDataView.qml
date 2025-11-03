pragma Singleton
import QtQuick
import "../datas" as Datas
import "../Api" as Api
// 图像标定核心工具：提供像素/世界/相机坐标互转及夹具查询
// 全局数据显示中心

QtObject {
  id: root

  // 标定图像宽高（像素）
  readonly property real imageWidth: Math.max(0, Datas.CalibrationData.imageWidth)
  readonly property real imageHeight: Math.max(0, Datas.CalibrationData.imageHeight)
  // 世界坐标范围与原点
  readonly property real worldWidth: Datas.CalibrationData.worldWidth
  readonly property real worldHeight: Datas.CalibrationData.worldHeight
  readonly property real originX: Datas.CalibrationData.originX
  readonly property real originY: Datas.CalibrationData.originY
  // 夹具集合（来自标定数据）
  readonly property var fixtures: Datas.CalibrationData.fixtures

  // 视图渲染区域尺寸（像素）
  property int viewWidth: 0
  property int viewHeight: 0
  // 鼠标在视图坐标系下的位置（未缩放）
  property point viewPixel: Qt.point(-1, -1)
  // 视图到图像的缩放系数
  readonly property real viewScaleX: viewWidth > 0 ? imageWidth / viewWidth : 0
  readonly property real viewScaleY: viewHeight > 0 ? imageHeight / viewHeight : 0

  // 当前光标像素/世界坐标
  property point cursorPixel: Qt.point(-1, -1)
  property point cursorWorld: Qt.point(0, 0)
  property bool cursorValid: false
  // 当前光标相机坐标（三维）
  property var cursorCamera: Qt.vector3d(0, 0, 0)
  property bool cursorCameraValid: false

  // 内部状态：相机坐标请求管理
  property point _pendingCameraPixel: Qt.point(-1, -1)
  property point _lastCameraPixel: Qt.point(-1, -1)
  property bool _cameraBusy: false
  property int _cameraRequestId: 0

  // 像素/世界尺度换算
  readonly property real worldPerPixelX: imageWidth > 0 ? worldWidth / imageWidth : 0
  readonly property real worldPerPixelY: imageHeight > 0 ? worldHeight / imageHeight : 0
  readonly property real pixelPerWorldX: worldWidth !== 0 ? imageWidth / (worldWidth || 1) : 0
  readonly property real pixelPerWorldY: worldHeight !== 0 ? imageHeight / (worldHeight || 1) : 0

  // 像素坐标 -> 世界坐标
  function imageToWorld(point) {
    if (!point)
      return { x: originX, y: originY }
    var px = Number(point.x !== undefined ? point.x : 0)
    var py = Number(point.y !== undefined ? point.y : 0)
    return {
      x: originX + px * worldPerPixelX,
      y: originY + py * worldPerPixelY
    }
  }

  // 世界坐标 -> 像素坐标
  function worldToImage(point) {
    if (!point)
      return { x: 0, y: 0 }
    var wx = Number(point.x !== undefined ? point.x : 0)
    var wy = Number(point.y !== undefined ? point.y : 0)
    return {
      x: (wx - originX) * pixelPerWorldX,
      y: (wy - originY) * pixelPerWorldY
    }
  }

  // 根据名称查找夹具
  function fixtureByName(name) {
    if (!fixtures || !name)
      return null
    for (var i = 0; i < fixtures.length; ++i) {
      var fixture = fixtures[i]
      if (fixture && fixture.name === name)
        return fixture
    }
    return null
  }

  // 夹具世界坐标矩形
  function fixtureRectWorld(fixture) {
    var target = fixture
    if (typeof fixture === "string")
      target = fixtureByName(fixture)
    if (!target || !target.rect)
      return { x: 0, y: 0, width: 0, height: 0 }
    var rect = target.rect
    var topLeft = imageToWorld({ x: rect.x || 0, y: rect.y || 0 })
    var bottomRight = imageToWorld({
      x: Number(rect.x || 0) + Number(rect.width || 0),
      y: Number(rect.y || 0) + Number(rect.height || 0)
    })
    return {
      x: topLeft.x,
      y: topLeft.y,
      width: bottomRight.x - topLeft.x,
      height: bottomRight.y - topLeft.y
    }
  }

  // 夹具旋转原点（世界坐标）
  function rotationOriginWorld(fixture) {
    var target = fixture
    if (typeof fixture === "string")
      target = fixtureByName(fixture)
    if (!target || !target.rotation_origin)
      return { x: originX, y: originY }
    return imageToWorld(target.rotation_origin)
  }

  // 更新光标数据（由视图调用）
  function setCursor(pixelPoint, worldPoint, valid) {
    if (!valid || !pixelPoint) {
      cursorPixel = Qt.point(-1, -1)
      cursorWorld = Qt.point(0, 0)
      cursorValid = false
      _resetCamera()
      return
    }

    var px = Qt.point(Number(pixelPoint.x || 0), Number(pixelPoint.y || 0))
    cursorPixel = px
    if (worldPoint) {
      cursorWorld = Qt.point(Number(worldPoint.x || 0), Number(worldPoint.y || 0))
    } else {
      var mapped = imageToWorld(px)
      cursorWorld = Qt.point(mapped.x, mapped.y)
    }
    cursorValid = true
    cursorCameraValid = false
    requestCameraSample(px)
  }

  function clearCursor() {
    setCursor(null, null, false)
  }

  function requestCameraSample(pixelPoint) {
    if (!pixelPoint) {
      _resetCamera()
      return
    }
    var ix = Math.round(Number(pixelPoint.x || 0))
    var iy = Math.round(Number(pixelPoint.y || 0))
    if (ix < 0 || iy < 0) {
      _resetCamera()
      return
    }

    var targetPixel = Qt.point(ix, iy)
    if (cursorCameraValid &&
        _lastCameraPixel.x === targetPixel.x &&
        _lastCameraPixel.y === targetPixel.y) {
      return
    }

    if (_cameraBusy) {
      _pendingCameraPixel = targetPixel
      return
    }

    _cameraBusy = true
    _pendingCameraPixel = Qt.point(-1, -1)
    _cameraRequestId += 1
    var requestId = _cameraRequestId
    var path = '/vision/pointcloud/pixel?x=' + ix + '&y=' + iy
    Api.ApiClient.get(path,
      function(resp) {
        _cameraBusy = false
        _applyCameraResponse(requestId, targetPixel, resp)
        _drainPendingCameraRequest()
      },
      function(status, message) {
        _cameraBusy = false
        // 仅当目标像素仍然有效时清空
        if (_isCurrentPixel(targetPixel)) {
          cursorCamera = Qt.vector3d(0, 0, 0)
          cursorCameraValid = false
        }
        _drainPendingCameraRequest()
      }
    )
  }

  function _applyCameraResponse(requestId, targetPixel, payload) {
    if (requestId !== _cameraRequestId)
      return
    if (!_isCurrentPixel(targetPixel))
      return
    if (!payload || !payload.camera) {
      cursorCamera = Qt.vector3d(0, 0, 0)
      cursorCameraValid = false
      return
    }
    var cam = payload.camera
    var cx = Number(cam.x)
    var cy = Number(cam.y)
    var cz = Number(cam.z)
    if (!(isFinite(cx) && isFinite(cy) && isFinite(cz))) {
      cursorCamera = Qt.vector3d(0, 0, 0)
      cursorCameraValid = false
      return
    }
    cursorCamera = Qt.vector3d(cx, cy, cz)
    cursorCameraValid = true
    _lastCameraPixel = Qt.point(targetPixel.x, targetPixel.y)
  }

  function _drainPendingCameraRequest() {
    if (_pendingCameraPixel.x >= 0 && _pendingCameraPixel.y >= 0) {
      var pending = Qt.point(_pendingCameraPixel.x, _pendingCameraPixel.y)
      _pendingCameraPixel = Qt.point(-1, -1)
      requestCameraSample(pending)
    }
  }

  function _isCurrentPixel(pixel) {
    var current = Qt.point(
      Math.round(Number(cursorPixel.x || 0)),
      Math.round(Number(cursorPixel.y || 0))
    )
    return current.x === pixel.x && current.y === pixel.y
  }

  function _resetCamera() {
    cursorCamera = Qt.vector3d(0, 0, 0)
    cursorCameraValid = false
    _pendingCameraPixel = Qt.point(-1, -1)
    _lastCameraPixel = Qt.point(-1, -1)
  }
}
