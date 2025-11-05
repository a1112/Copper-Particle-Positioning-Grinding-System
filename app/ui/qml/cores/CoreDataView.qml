pragma Singleton
import QtQuick
import "../datas" as Datas
import "../Api" as Api
// 图像标定核心工具：提供像素/世界/相机坐标互转及夹具查询
// 全局数据显示中心

Item {
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

  // 当前光标像素/机床坐标
  property point cursorPixel: Qt.point(-1, -1)
  property var cursorMachine: _nanVector()
  readonly property var cursorWorld: cursorMachine
  property bool cursorValid: false
  property var cursorCamera: _nanVector()
  property bool cursorCameraValid: false
  // 当前机床转换矩阵（4x4）
  property var machineMatrix: []

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
  function _nanVector() {
    return Qt.vector3d(Number.NaN, Number.NaN, Number.NaN)
  }

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
      cursorMachine = _nanVector()
      cursorValid = false
      _resetCamera()
      return
    }

    var px = Qt.point(Number(pixelPoint.x || 0), Number(pixelPoint.y || 0))
    cursorPixel = px
    if (worldPoint) {
      var wx = Number(worldPoint.x || 0)
      var wy = Number(worldPoint.y || 0)
      var wz = Number(worldPoint.z || 0)
      cursorMachine = Qt.vector3d(wx, wy, wz)
    } else {
      var mapped = imageToWorld(px)
      cursorMachine = Qt.vector3d(mapped.x, mapped.y, 0)
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
          cursorCamera = _nanVector()
          cursorCameraValid = false
          cursorMachine = _nanVector()
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
      cursorCamera = _nanVector()
      cursorCameraValid = false
      cursorMachine = _nanVector()
      return
    }
    var cam = payload.camera
    var cx = Number(cam.x)
    var cy = Number(cam.y)
    var cz = Number(cam.z)
    if (!(isFinite(cx) && isFinite(cy) && isFinite(cz))) {
      cursorCamera = _nanVector()
      cursorCameraValid = false
      cursorMachine = _nanVector()
      return
    }
    if (Math.abs(cx) <= 1e-6 && Math.abs(cy) <= 1e-6 && Math.abs(cz) <= 1e-6) {
      cursorCamera = _nanVector()
      cursorCameraValid = false
      cursorMachine = _nanVector()
      return
    }
    cursorCamera = Qt.vector3d(cx, cy, cz)
    cursorCameraValid = true
    _lastCameraPixel = Qt.point(targetPixel.x, targetPixel.y)
    var machineVec = _transformCameraToMachine(cursorCamera)
    if (machineVec)
      cursorMachine = machineVec
    else
      cursorMachine = _nanVector()
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
    cursorCamera = _nanVector()
    cursorCameraValid = false
    _pendingCameraPixel = Qt.point(-1, -1)
    _lastCameraPixel = Qt.point(-1, -1)
    cursorMachine = _nanVector()
  }

  function _machineFromPixel(px) {
    if (!px || px.x === undefined || px.y === undefined)
      return Qt.vector3d(0, 0, 0)
    var mapped = imageToWorld({ x: Number(px.x), y: Number(px.y) })
    return Qt.vector3d(Number(mapped.x || 0), Number(mapped.y || 0), 0)
  }

  function _transformCameraToMachine(cameraVec) {
    if (!cameraVec)
      return null
    if (!machineMatrix || machineMatrix.length !== 4)
      return null
    var rows = machineMatrix
    for (var i = 0; i < 4; ++i) {
      if (!rows[i] || rows[i].length < 4)
        return null
    }
    var x = Number(cameraVec.x || 0)
    var y = Number(cameraVec.y || 0)
    var z = Number(cameraVec.z || 0)
    var w = 1.0
    var mx = rows[0][0] * x + rows[0][1] * y + rows[0][2] * z + rows[0][3] * w
    var my = rows[1][0] * x + rows[1][1] * y + rows[1][2] * z + rows[1][3] * w
    var mz = rows[2][0] * x + rows[2][1] * y + rows[2][2] * z + rows[2][3] * w
    return Qt.vector3d(mx, my, mz)
  }

  function _normaliseMatrix(value) {
    if (!value)
      return []
    var rows = []
    if (Array.isArray(value)) {
      if (Array.isArray(value[0])) {
        for (var i = 0; i < value.length && rows.length < 4; ++i) {
          var row = value[i]
          if (!Array.isArray(row))
            continue
          var copy = [Number(row[0] || 0), Number(row[1] || 0), Number(row[2] || 0), Number(row[3] || 0)]
          rows.push(copy)
        }
      } else {
        var flat = []
        for (var j = 0; j < value.length; ++j)
          flat.push(Number(value[j] || 0))
        if (flat.length === 16) {
          for (var r = 0; r < 4; ++r)
            rows.push(flat.slice(r * 4, r * 4 + 4))
        } else if (flat.length === 12) {
          for (var rr = 0; rr < 4; ++rr) {
            var base = flat.slice(rr * 3, rr * 3 + 3)
            rows.push([base[0] || 0, base[1] || 0, base[2] || 0, rr < 3 ? 0 : 1])
          }
        }
      }
    } else if (typeof value === "object") {
      var values = []
      for (var key in value) {
        if (value.hasOwnProperty(key))
          values.push(Number(value[key] || 0))
      }
      if (values.length === 16) {
        for (var h = 0; h < 4; ++h)
          rows.push(values.slice(h * 4, h * 4 + 4))
      }
    }
    if (rows.length === 4) {
      for (var n = 0; n < 4; ++n) {
        if (!rows[n] || rows[n].length < 4)
          rows[n] = [0, 0, 0, n < 3 ? 0 : 1]
      }
      rows[3][0] = 0
      rows[3][1] = 0
      rows[3][2] = 0
      rows[3][3] = 1
    }
    return rows.length === 4 ? rows : []
  }

  Connections {

    target: Datas.TaskDatas
    function onGcodeDataChanged() {
      var gcode = Datas.TaskDatas.gcodeData || {}
      var matrix = gcode.camera_to_robot_matrix || gcode.machine_matrix || gcode.machine || null
      machineMatrix = _normaliseMatrix(matrix)
      if (!cursorCameraValid && cursorValid)
        cursorMachine = _machineFromPixel(cursorPixel)
      else if (cursorCameraValid) {
        var machineVec = _transformCameraToMachine(cursorCamera)
        if (machineVec)
          cursorMachine = machineVec
      }
    }
  }

  Component.onCompleted: {
    var gcode = Datas.TaskDatas.gcodeData || {}
    var matrix = gcode.camera_to_robot_matrix || gcode.machine_matrix || gcode.machine || null
    machineMatrix = _normaliseMatrix(matrix)
    if (cursorValid)
      cursorMachine = _machineFromPixel(cursorPixel)
  }
}
