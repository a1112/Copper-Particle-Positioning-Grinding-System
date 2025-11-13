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
}
