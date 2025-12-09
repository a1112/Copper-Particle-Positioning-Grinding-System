import QtQuick
import QtQuick.Controls

import "../../../cores" as Cores

Item {
  id: overlay
  width: parent.width
  height: parent.height

  // Legacy fallback parameters (grid-based fixtures)
  property int columns: 4
  property int rows: 4
  property real imageWidth: 640
  property real imageHeight: 360
  property real pixelSizeMm: 0.2
  property real fixtureSizeMm: 8
  property real fixtureMarginMm: 6
  property real scaleX: 1.0
  property real scaleY: 1.0

  // Calibration-aware fixtures list ({ name, rotation_origin:{x,y}, rect:{x,y,width,height} })
  property var fixtures: []

  readonly property real fixtureWidthPx: fixtureSizeMm / (pixelSizeMm > 0 ? pixelSizeMm : 1)
  readonly property real fixtureHeightPx: fixtureSizeMm / (pixelSizeMm > 0 ? pixelSizeMm : 1)
  readonly property real marginPx: fixtureMarginMm / (pixelSizeMm > 0 ? pixelSizeMm : 1)
  readonly property int fixturesPerEdge: Math.max(1, columns)
  readonly property bool hasCalibrationFixtures: fixtures && fixtures.length > 0

  readonly property var fixturePositions: {
    if (hasCalibrationFixtures)
      return []
    var positions = []
    var n = fixturesPerEdge
    var stepX = n > 0 ? (imageWidth - marginPx * 2) / (n + 1) : 0
    var stepY = n > 0 ? (imageHeight - marginPx * 2) / (n + 1) : 0

    for (var i = 0; i < n; ++i) {
      var offsetX = marginPx + (i + 1) * stepX
      positions.push({ x: offsetX, y: marginPx, edge: "top", index: i })
    }

    for (var j = 0; j < n; ++j) {
      var offsetXBottom = marginPx + (j + 1) * stepX
      positions.push({ x: offsetXBottom, y: imageHeight - marginPx, edge: "bottom", index: j })
    }

    for (var k = 0; k < n; ++k) {
      var offsetY = marginPx + (k + 1) * stepY
      positions.push({ x: marginPx, y: offsetY, edge: "left", index: k })
    }

    for (var m = 0; m < n; ++m) {
      var offsetYRight = marginPx + (m + 1) * stepY
      positions.push({ x: imageWidth - marginPx, y: offsetYRight, edge: "right", index: m })
    }
    return positions
  }

  Repeater {
    id: fixtureRepeater
    model: overlay.hasCalibrationFixtures ? overlay.fixtures.length : overlay.fixturePositions.length
    delegate: Item {
      readonly property bool useCalibration: overlay.hasCalibrationFixtures
      readonly property var fixtureSource: useCalibration ? overlay.fixtures : overlay.fixturePositions
      readonly property var fixture: (fixtureSource && fixtureSource[index]) ? fixtureSource[index] : ({})
      readonly property var rectData: (useCalibration && fixture && fixture.rect) ? fixture.rect : null

      width: useCalibration
             ? Number((rectData && rectData.width) || 0) * overlay.scaleX
             : overlay.fixtureWidthPx * overlay.scaleX
      height: useCalibration
              ? Number((rectData && rectData.height) || 0) * overlay.scaleY
              : overlay.fixtureHeightPx * overlay.scaleY
      x: useCalibration
         ? Number((rectData && rectData.x) || 0) * overlay.scaleX
         : Number(fixture.x || 0) * overlay.scaleX - width / 2
      y: useCalibration
         ? Number((rectData && rectData.y) || 0) * overlay.scaleY
         : Number(fixture.y || 0) * overlay.scaleY - height / 2

      Rectangle {
        anchors.fill: parent
        color: Qt.rgba(0.15, 0.8, 0.95, 0.18)
        border.color: Qt.rgba(0.0, 0.9, 1.0, 0.6)
        border.width: 1
        radius: Math.min(width, height) * 0.15

        Label {
          anchors.centerIn: parent
          color: Cores.CoreStyle.text
          font.pixelSize: 11
          text: parent.parent.useCalibration
                ? (parent.parent.fixture && parent.parent.fixture.name
                   ? parent.parent.fixture.name
                   : qsTr("夹具%1").arg(index + 1))
                : (function() {
                    var edge = parent.parent.fixture && parent.parent.fixture.edge ? parent.parent.fixture.edge : ""
                    var edgeLabel = edge === "top" ? qsTr("上")
                                    : edge === "bottom" ? qsTr("下")
                                    : edge === "left" ? qsTr("左")
                                    : qsTr("右")
                    var fixtureIndex = parent.parent.fixture && parent.parent.fixture.index !== undefined
                                       ? parent.parent.fixture.index
                                       : index
                    return qsTr("%1夹具%2").arg(edgeLabel).arg(fixtureIndex + 1)
                  })()
        }

        Rectangle {
          visible: parent.parent.useCalibration && parent.parent.fixture && parent.parent.fixture.rotation_origin
          width: 6
          height: 6
          radius: 3
          color: "#f59e0b"
          border.color: "#d97706"
          border.width: 1
          readonly property real targetX: Number((parent.parent.fixture && parent.parent.fixture.rotation_origin && parent.parent.fixture.rotation_origin.x) || 0) * overlay.scaleX
          readonly property real targetY: Number((parent.parent.fixture && parent.parent.fixture.rotation_origin && parent.parent.fixture.rotation_origin.y) || 0) * overlay.scaleY
          x: targetX - parent.parent.x - width / 2
          y: targetY - parent.parent.y - height / 2
        }
      }
    }
  }
}
