import QtQuick
import "../../../datas" as Datas

// 图像标定核心工具：提供像素与世界坐标互转及夹具查询
QtObject {
  id: root

  // 标定图像宽度（像素）
  readonly property real imageWidth: Math.max(0, Datas.CalibrationData.imageWidth)
  // 标定图像高度（像素）
  readonly property real imageHeight: Math.max(0, Datas.CalibrationData.imageHeight)
  // 世界坐标宽度
  readonly property real worldWidth: Datas.CalibrationData.worldWidth
  // 世界坐标高度
  readonly property real worldHeight: Datas.CalibrationData.worldHeight
  // 世界坐标原点 X
  readonly property real originX: Datas.CalibrationData.originX
  // 世界坐标原点 Y
  readonly property real originY: Datas.CalibrationData.originY
  // 夹具集合（来自标定数据）
  readonly property var fixtures: Datas.CalibrationData.fixtures

  // 单位像素对应的世界坐标距离（X 方向）
  readonly property real worldPerPixelX: imageWidth > 0 ? worldWidth / imageWidth : 0
  // 单位像素对应的世界坐标距离（Y 方向）
  readonly property real worldPerPixelY: imageHeight > 0 ? worldHeight / imageHeight : 0
  // 单位世界坐标对应的像素距离（X 方向）
  readonly property real pixelPerWorldX: worldWidth !== 0 ? imageWidth / (worldWidth || 1) : 0
  // 单位世界坐标对应的像素距离（Y 方向）
  readonly property real pixelPerWorldY: worldHeight !== 0 ? imageHeight / (worldHeight || 1) : 0

  // 像素坐标转换到世界坐标
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

  // 世界坐标转换回像素坐标
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

  // 获取夹具在世界坐标系下的矩形
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

  // 获取夹具旋转中心在世界坐标系的位置
  function rotationOriginWorld(fixture) {
    var target = fixture
    if (typeof fixture === "string")
      target = fixtureByName(fixture)
    if (!target || !target.rotation_origin)
      return { x: originX, y: originY }
    return imageToWorld(target.rotation_origin)
  }
}
