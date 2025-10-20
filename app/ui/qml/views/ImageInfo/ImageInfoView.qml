import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "head"
import "../../Api" as Api
import "../Base"
import "../../cores" as Cores
import "../../components/btns" as Btns

import "view2d"
import "view3d"
BaseCard {
  id: root
  property int refreshMs: 150
  property var pathPoints: []
  readonly property int maxPath: 2000
  property url meshSource3d: ""
  property real imageWidthPx: 640
  property real imageHeightPx: 360
  property real pixelSizeMm: 0.2
  property var toolWorldPosition: ({})
  property int fixtureColumns: 4
  property int fixtureRows: 4
  property real fixtureSizeMm: 8
  property real fixtureMarginMm: 6
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
      }
      View3D{
        meshSource: root.meshSource3d
      }
    }
  }
}
