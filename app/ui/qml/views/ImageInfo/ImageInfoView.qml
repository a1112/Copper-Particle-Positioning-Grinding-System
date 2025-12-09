import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "head"
import "../../Api" as Api
import "../Base"
import "../../cores" as Cores
import "../../datas" as Datas
import "../../components/btns" as Btns
import "." as ImageInfo
import "view2d"
import "view3d"
BaseCard {
  id: root

  property var viewCore: ImageInfo.ViewCore
  property int refreshMs: 150
  property var pathPoints: Cores.CoreCutting.displayImagePath || []
  readonly property int maxPath: 200
  property url meshSource3d: Cores.CoreState.current3dModelSource
  property real imageWidthPx: Cores.CoreDataView.imageWidth
  property real imageHeightPx: Cores.CoreDataView.imageHeight
  property real pixelSizeMm: (Cores.CoreDataView.imageWidth > 0) ? Cores.CoreDataView.worldWidth / Cores.CoreDataView.imageWidth : 0
  property var toolWorldPosition: ({})
  property int fixtureColumns: 4
  property int fixtureRows: 4
  property real fixtureSizeMm: 8
  property real fixtureMarginMm: 6
  property var calibrationFixtures: Cores.CoreDataView.fixtures
  property var imageDataCore: Cores.CoreDataView
  readonly property var algResultData: {
    var gcode = Datas.TaskDatas.gcodeData || {}
    if (gcode && gcode.alg_result !== undefined && gcode.alg_result !== null)
      return gcode.alg_result
    if (gcode && gcode.algResult !== undefined && gcode.algResult !== null)
      return gcode.algResult
    return null
  }
  property var defectAreaRects: defectArray(["lzRects", "lz_rects"])
  property var defectSingleRects: defectArray(["singleLzRects", "single_lz_rects"])
  implicitHeight: col.implicitHeight + 16

  function defectArray(fieldNames) {
    var alg = algResultData
    if (!alg || typeof alg !== "object")
      return []
    var defect = alg.defectResult || alg.defect_result
    if (!defect || typeof defect !== "object")
      return []
    for (var i = 0; i < fieldNames.length; ++i) {
      var key = fieldNames[i]
      if (defect[key] && Array.isArray(defect[key]))
        return defect[key]
    }
    return []
  }

  function _parseNumeric(value) {
    if (value === undefined || value === null)
      return NaN
    var direct = Number(value)
    if (!isNaN(direct))
      return direct
    if (typeof value === "string") {
      var cleaned = value.replace(/[^0-9+-.]/g, "")
      if (cleaned.length === 0)
        return NaN
      var parsed = Number(cleaned)
      if (!isNaN(parsed))
        return parsed
    }
    return NaN
  }

  function _resolveToolDiameter(payload) {
    var candidates = []
    if (payload) {
      if (payload.tool_diameter !== undefined)
        candidates.push(payload.tool_diameter)
      if (payload.toolDiameter !== undefined)
        candidates.push(payload.toolDiameter)
      if (payload.cutter_diameter !== undefined)
        candidates.push(payload.cutter_diameter)
      if (payload.spindle && payload.spindle.tool_diameter !== undefined)
        candidates.push(payload.spindle.tool_diameter)
      if (payload.tool && payload.tool.diameter !== undefined)
        candidates.push(payload.tool.diameter)
    }
    candidates.push(Datas.ToolInfoData.toolDiameter)
    for (var i = 0; i < candidates.length; ++i) {
      var numeric = _parseNumeric(candidates[i])
      if (!isNaN(numeric) && numeric > 0)
        return numeric
    }
    return NaN
  }

  function _buildToolSnapshot(payload) {
    var message = payload
    if (!message || typeof message !== "object")
      message = Datas.StatusDatas.lastMessage
    if (!message || typeof message !== "object")
      return {}

    var pose = message.tool_position || message.toolPosition || message.position
    if (!pose || typeof pose !== "object")
      return {}

    var xValue = pose.x !== undefined ? pose.x : (pose.X !== undefined ? pose.X : pose[0])
    var yValue = pose.y !== undefined ? pose.y : (pose.Y !== undefined ? pose.Y : pose[1])
    var zValue = pose.z !== undefined ? pose.z : (pose.Z !== undefined ? pose.Z : pose[2])

    var x = _parseNumeric(xValue)
    var y = _parseNumeric(yValue)
    if (isNaN(x) || isNaN(y))
      return {}

    var snapshot = { x: x, y: y }
    var z = _parseNumeric(zValue)
    if (!isNaN(z))
      snapshot.z = z

    var rpmSources = [
          message.spindle_rpm,
          message.spindleRPM,
          message.spindle_speed,
          message.spindle ? message.spindle.rpm : undefined
        ]
    for (var r = 0; r < rpmSources.length; ++r) {
      var rpmValue = _parseNumeric(rpmSources[r])
      if (!isNaN(rpmValue)) {
        snapshot.rpm = rpmValue
        break
      }
    }

    var diameter = _resolveToolDiameter(message)
    if (!isNaN(diameter))
      snapshot.diameter = diameter

    return snapshot
  }

  function _refreshToolWorldPosition(payload) {
    var snapshot = _buildToolSnapshot(payload)
    toolWorldPosition = snapshot
  }

  ColumnLayout {
    id:col
    anchors.fill: parent
    anchors.margins: 8
    spacing: 6
    ViewHead{}
    StackLayout{
      id: viewStack
      Layout.fillWidth: true
      Layout.fillHeight: true
      currentIndex: Cores.CoreState.realViewIndex
      View2D{
        imageWidth: root.imageWidthPx
        imageHeight: root.imageHeightPx
        pixelSizeMm: root.pixelSizeMm
        pathPoints: root.pathPoints
        toolWorldPosition: root.toolWorldPosition
        fixtureColumns: root.fixtureColumns
        fixtureRows: root.fixtureRows
        fixtureSizeMm: root.fixtureSizeMm
        fixtureMarginMm: root.fixtureMarginMm
        fixtures: root.calibrationFixtures
        defectAreaRects: root.defectAreaRects
        defectSingleRects: root.defectSingleRects
        calibrationCore: root.imageDataCore

      }
      View3D{
        meshSource: root.meshSource3d
      }
    }
  }

  Connections {
    target: Datas.StatusDatas
    function onMessageReceived(payload) {
      root._refreshToolWorldPosition(payload)
    }
  }

  Connections {
    target: Datas.ToolInfoData
    function onToolDiameterChanged() {
      root._refreshToolWorldPosition(Datas.StatusDatas.lastMessage)
    }
  }

  Component.onCompleted: {
    _refreshToolWorldPosition(Datas.StatusDatas.lastMessage)
  }
}
