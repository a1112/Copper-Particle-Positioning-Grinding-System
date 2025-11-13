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
  property var cameraMatrix: []

  property var _cameraPixelCache: ({})
  property var _cameraPixelPending: ({})
  property string statusMessage: ""

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

  function _normaliseVector3(value) {
    if (!value)
      return { x: 0, y: 0, z: 0 }
    var xVal = value.x !== undefined ? Number(value.x) : Number(value.width || 0)
    var yVal = value.y !== undefined ? Number(value.y) : Number(value.height || 0)
    var zRaw = value.z !== undefined ? value.z : (value.depth !== undefined ? value.depth : 0)
    var zVal = Number(zRaw)
    return {
      x: isFinite(xVal) ? xVal : 0,
      y: isFinite(yVal) ? yVal : 0,
      z: isFinite(zVal) ? zVal : 0
    }
  }

  function _formatNumberForQuery(value) {
    var num = Number(value)
    if (!isFinite(num))
      num = 0
    return num.toFixed(6)
  }

  function _cameraLookupKey(cameraPoint) {
    var vec = _normaliseVector3(cameraPoint)
    return _formatNumberForQuery(vec.x) + "|" + _formatNumberForQuery(vec.y) + "|" + _formatNumberForQuery(vec.z)
  }

  function clearCameraPixelCache() {
    _cameraPixelCache = ({})
    _cameraPixelPending = ({})
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
    var recordIdValue = Number(Datas.TaskDatas.latestRecordId || 0)
    if (!isFinite(recordIdValue) || recordIdValue < 0)
      recordIdValue = 0
    var path = '/vision/pointcloud/pixel?x=' + ix + '&y=' + iy
    if (recordIdValue > 0)
      path += '&record_id=' + Math.round(recordIdValue)
    Api.ApiClient.getQuiet(path,
      function(resp) {
        _cameraBusy = false
        statusMessage = ""
        _applyCameraResponse(requestId, targetPixel, resp)
        _drainPendingCameraRequest()
      },
      function(status, message) {
        _cameraBusy = false
        if (status === 404 && String(message).indexOf("Point cloud component") !== -1)
          statusMessage = qsTr("采集识别中...")
        else
          statusMessage = ""
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
    statusMessage = ""
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
    statusMessage = ""
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

  function _transformMachineToCamera(machineVec) {
    if (!machineVec)
      return null
    if (!cameraMatrix || cameraMatrix.length !== 4)
      return null
    var rows = cameraMatrix
    for (var i = 0; i < 4; ++i) {
      if (!rows[i] || rows[i].length < 4)
        return null
    }
    var x = Number(machineVec.x !== undefined ? machineVec.x : machineVec[0] || 0)
    var y = Number(machineVec.y !== undefined ? machineVec.y : machineVec[1] || 0)
    var z = Number(machineVec.z !== undefined ? machineVec.z : machineVec[2] || 0)
    var w = 1.0
    var cx = rows[0][0] * x + rows[0][1] * y + rows[0][2] * z + rows[0][3] * w
    var cy = rows[1][0] * x + rows[1][1] * y + rows[1][2] * z + rows[1][3] * w
    var cz = rows[2][0] * x + rows[2][1] * y + rows[2][2] * z + rows[2][3] * w
    return { x: cx, y: cy, z: cz }
  }

  function cameraToMachine(cameraPoint) {
    var vec = _normaliseVector3(cameraPoint)
    var transformed = _transformCameraToMachine(Qt.vector3d(vec.x, vec.y, vec.z))
    if (transformed)
      return { x: transformed.x, y: transformed.y, z: transformed.z }
    return vec
  }

  function machineToCamera(machinePoint) {
    var vec = _normaliseVector3(machinePoint)
    var mapped = _transformMachineToCamera(vec)
    if (mapped)
      return mapped
    return vec
  }

  function cameraToPixel(cameraPoint, options) {
    var opts = options || {}
    var vec = _normaliseVector3(cameraPoint)
    var recordIdValue = opts.recordId !== undefined && opts.recordId !== null
                        ? Number(opts.recordId)
                        : Number(Datas.TaskDatas.latestRecordId || 0)
    if (!isFinite(recordIdValue) || recordIdValue < 0)
      recordIdValue = 0
    var recordKey = recordIdValue > 0 ? Math.round(recordIdValue) : 0
    var radiusKey = (opts.maxRadius !== undefined && opts.maxRadius !== null)
                    ? _formatNumberForQuery(opts.maxRadius)
                    : ""
    var distanceKey = (opts.maxDistance !== undefined && isFinite(opts.maxDistance))
                      ? _formatNumberForQuery(opts.maxDistance)
                      : ""
    var key = String(recordKey) + "|" + radiusKey + "|" + distanceKey + "|" + _cameraLookupKey(vec)

    if (_cameraPixelCache.hasOwnProperty(key)) {
      var cached = _cameraPixelCache[key]
      return Promise.resolve(Qt.point(cached.x, cached.y))
    }
    if (_cameraPixelPending.hasOwnProperty(key))
      return _cameraPixelPending[key]

    var params = [
      "x=" + encodeURIComponent(_formatNumberForQuery(vec.x)),
      "y=" + encodeURIComponent(_formatNumberForQuery(vec.y)),
      "z=" + encodeURIComponent(_formatNumberForQuery(vec.z))
    ]
    if (opts.maxRadius !== undefined && opts.maxRadius !== null)
      params.push("max_radius=" + encodeURIComponent(_formatNumberForQuery(opts.maxRadius)))
    if (recordKey > 0)
      params.push("record_id=" + encodeURIComponent(String(recordKey)))

    var path = "/vision/pointcloud/lookup?" + params.join("&")

    var promise = new Promise(function(resolve) {
      Api.ApiClient.getQuiet(path,
        function(resp) {
          delete _cameraPixelPending[key]
          if (!resp || !resp.pixel || resp.pixel.x === undefined || resp.pixel.y === undefined) {
            resolve(Qt.point(-1, -1))
            return
          }

          var distance = resp.distance !== undefined ? Number(resp.distance) : 0
          if (opts.maxDistance !== undefined && isFinite(opts.maxDistance) && distance > opts.maxDistance) {
            resolve(Qt.point(-1, -1))
            return
          }

          var pxValue = Number(resp.pixel.x)
          var pyValue = Number(resp.pixel.y)
          if (!isFinite(pxValue) || !isFinite(pyValue)) {
            resolve(Qt.point(-1, -1))
            return
          }
          var cacheEntry = { x: pxValue, y: pyValue, distance: distance, record: recordKey }
          _cameraPixelCache[key] = cacheEntry
          statusMessage = ""
          resolve(Qt.point(pxValue, pyValue))
        },
        function(status, message) {
          console.warn("cameraToPixel lookup failed", status, message)
          delete _cameraPixelPending[key]
          if (status === 404 && String(message).indexOf("Point cloud component") !== -1)
            statusMessage = qsTr("采集识别中...")
          else
            statusMessage = ""
          resolve(Qt.point(-1, -1))
        }
      )
    })

    _cameraPixelPending[key] = promise
    return promise
  }

  function machineToPixel(machinePoint, options) {
    var camera = machineToCamera(machinePoint)
    return cameraToPixel(camera, options)
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

  function _invertMatrix4(matrix) {
    if (!matrix || matrix.length !== 4)
      return []
    var size = 4
    var src = []
    var inv = []
    for (var r = 0; r < size; ++r) {
      var row = matrix[r]
      if (!row || row.length < 4)
        return []
      for (var c = 0; c < size; ++c) {
        src[r * size + c] = Number(row[c] || 0)
        inv[r * size + c] = r === c ? 1 : 0
      }
    }

    for (var col = 0; col < size; ++col) {
      var pivotRow = col
      var pivotValue = src[col * size + col]
      var maxAbs = Math.abs(pivotValue)
      for (var rowSearch = col + 1; rowSearch < size; ++rowSearch) {
        var candidate = Math.abs(src[rowSearch * size + col])
        if (candidate > maxAbs) {
          maxAbs = candidate
          pivotRow = rowSearch
        }
      }
      if (maxAbs < 1e-9)
        return []

      if (pivotRow !== col) {
        for (var swapIndex = 0; swapIndex < size; ++swapIndex) {
          var srcTmp = src[col * size + swapIndex]
          src[col * size + swapIndex] = src[pivotRow * size + swapIndex]
          src[pivotRow * size + swapIndex] = srcTmp

          var invTmp = inv[col * size + swapIndex]
          inv[col * size + swapIndex] = inv[pivotRow * size + swapIndex]
          inv[pivotRow * size + swapIndex] = invTmp
        }
      }

      pivotValue = src[col * size + col]
      var invPivot = 1.0 / pivotValue
      for (var scaleIndex = 0; scaleIndex < size; ++scaleIndex) {
        src[col * size + scaleIndex] *= invPivot
        inv[col * size + scaleIndex] *= invPivot
      }

      for (var rowElim = 0; rowElim < size; ++rowElim) {
        if (rowElim === col)
          continue
        var factor = src[rowElim * size + col]
        if (Math.abs(factor) < 1e-9)
          continue
        for (var elimIndex = 0; elimIndex < size; ++elimIndex) {
          src[rowElim * size + elimIndex] -= factor * src[col * size + elimIndex]
          inv[rowElim * size + elimIndex] -= factor * inv[col * size + elimIndex]
        }
      }
    }

    var result = []
    for (var outRow = 0; outRow < size; ++outRow) {
      var resultRow = []
      for (var outCol = 0; outCol < size; ++outCol)
        resultRow.push(inv[outRow * size + outCol])
      result.push(resultRow)
    }
    return result
  }

  Connections {

    target: Datas.TaskDatas
    function onGcodeDataChanged() {
      var gcode = Datas.TaskDatas.gcodeData || {}
      var matrix = gcode.camera_to_robot_matrix || gcode.machine_matrix || gcode.machine || null
      var normalized = _normaliseMatrix(matrix)
      machineMatrix = normalized
      cameraMatrix = normalized.length === 4 ? _invertMatrix4(normalized) : []
      clearCameraPixelCache()
      if (!cursorCameraValid && cursorValid)
        cursorMachine = _machineFromPixel(cursorPixel)
      else if (cursorCameraValid) {
        var machineVec = _transformCameraToMachine(cursorCamera)
        if (machineVec)
          cursorMachine = machineVec
      }
    }
    function onLatestRecordIdChanged() {
      clearCameraPixelCache()
    }
  }

  Component.onCompleted: {
    var gcode = Datas.TaskDatas.gcodeData || {}
    var matrix = gcode.camera_to_robot_matrix || gcode.machine_matrix || gcode.machine || null
    var normalized = _normaliseMatrix(matrix)
    machineMatrix = normalized
    cameraMatrix = normalized.length === 4 ? _invertMatrix4(normalized) : []
    clearCameraPixelCache()
    if (cursorValid)
      cursorMachine = _machineFromPixel(cursorPixel)
  }

  Connections {
    target: Datas.CalibrationData
    ignoreUnknownSignals: true
    function onImageWidthChanged() { clearCameraPixelCache() }
    function onImageHeightChanged() { clearCameraPixelCache() }
    function onOriginXChanged() { clearCameraPixelCache() }
    function onOriginYChanged() { clearCameraPixelCache() }
  }
}
