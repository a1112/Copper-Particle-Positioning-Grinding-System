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
  property var calibrationFixtures: Datas.CuttingDatas.fixtures
  property var imageDataCore: Cores.CoreDataView
  implicitHeight: col.implicitHeight + 16

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
        calibrationCore: root.imageDataCore

      }
      View3D{
        meshSource: root.meshSource3d
      }
    }
  }
}
