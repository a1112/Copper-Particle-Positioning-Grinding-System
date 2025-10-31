pragma Singleton
import QtQuick

// 标定数据中心存储，统一提供图像尺寸、世界尺寸、原点与夹具信息
Item {
  id: root

  // 图像宽度（像素）
  readonly property alias imageWidth: _state.imageWidth
  // 图像高度（像素）
  readonly property alias imageHeight: _state.imageHeight

  // 世界坐标宽度（毫米或配置单位）
  readonly property alias worldWidth: _state.worldWidth
  // 世界坐标高度（毫米或配置单位）
  readonly property alias worldHeight: _state.worldHeight

  // 标定原点 X 坐标（世界坐标系）
  readonly property alias originX: _state.originX
  // 标定原点 Y 坐标（世界坐标系）
  readonly property alias originY: _state.originY
  // 夹具列表，每项包含 name / rotation_origin / rect
  readonly property alias fixtures: _state.fixtures

  // 内部可写状态对象，集中管理原始数据
  QtObject {
    id: _state
    // 默认图像宽度
    property real imageWidth: 0
    // 默认图像高度
    property real imageHeight: 0
    // 默认世界坐标宽度
    property real worldWidth: 0
    // 默认世界坐标高度
    property real worldHeight: 0
    // 默认原点 X
    property real originX: 0
    // 默认原点 Y
    property real originY: 0

    // 夹具数组（深拷贝保证外部不可修改）
    property var fixtures: []
  }

  // 应用后端下发的标定快照
  function applySnapshot(payload) {
    if (!payload)
      return
    var meta = payload
    try {
      // 解析图像尺寸
      if (meta.image !== undefined) {
        var img = meta.image
        if (img.width !== undefined)
          _state.imageWidth = Number(img.width)
        if (img.height !== undefined)
          _state.imageHeight = Number(img.height)
      } else {
        if (meta.image_width !== undefined)
          _state.imageWidth = Number(meta.image_width)
        if (meta.image_height !== undefined)
          _state.imageHeight = Number(meta.image_height)
      }

      // 解析世界尺寸
      if (meta.world !== undefined) {
        var world = meta.world
        if (world.width !== undefined)
          _state.worldWidth = Number(world.width)
        if (world.height !== undefined)
          _state.worldHeight = Number(world.height)
      } else {
        if (meta.world_width !== undefined)
          _state.worldWidth = Number(meta.world_width)
        if (meta.world_height !== undefined)
          _state.worldHeight = Number(meta.world_height)
      }

      // 解析原点
      var origin = meta.origin || {}
      if (origin.x !== undefined)
        _state.originX = Number(origin.x)
      if (origin.y !== undefined)
        _state.originY = Number(origin.y)
      if (meta.origin_x !== undefined)
        _state.originX = Number(meta.origin_x)
      if (meta.origin_y !== undefined)
        _state.originY = Number(meta.origin_y)

      // 解析夹具信息（深拷贝以防外部修改内部状态）
      if (meta.fixtures !== undefined && meta.fixtures instanceof Array)
        _state.fixtures = JSON.parse(JSON.stringify(meta.fixtures))
      else
        _state.fixtures = []
    } catch (err) {
      console.warn("CalibrationData.applySnapshot failed", err)
    }
  }

  // 重置为默认值
  function reset() {
    _state.imageWidth = 0
    _state.imageHeight = 0
    _state.worldWidth = 0
    _state.worldHeight = 0
    _state.originX = 0
    _state.originY = 0
    _state.fixtures = []
  }
}
