import QtQuick
import QtQuick.Controls

import "../../../cores" as Cores

Item {
  id: overlay
  anchors.fill: parent

  property int columns: 4            // clamps per edge
  property int rows: 4               // unused but kept for compatibility
  property real imageWidth: 640
  property real imageHeight: 360
  property real pixelSizeMm: 0.2
  property real fixtureSizeMm: 8
  property real fixtureMarginMm: 6
  property real scaleX: 1.0
  property real scaleY: 1.0

  readonly property real fixtureWidthPx: fixtureSizeMm / pixelSizeMm
  readonly property real fixtureHeightPx: fixtureSizeMm / pixelSizeMm
  readonly property real marginPx: fixtureMarginMm / pixelSizeMm
  readonly property int fixturesPerEdge: Math.max(1, columns)

  readonly property var fixturePositions: {
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
    positions
  }

  Repeater {
    id: fixtureRepeater
    model: overlay.fixturePositions.length
    delegate: Rectangle {
      readonly property var fixture: overlay.fixturePositions[index]
      width: overlay.fixtureWidthPx * overlay.scaleX
      height: overlay.fixtureHeightPx * overlay.scaleY
      x: fixture.x * overlay.scaleX - width / 2
      y: fixture.y * overlay.scaleY - height / 2
      color: Qt.rgba(0.15, 0.8, 0.95, 0.18)
      border.color: Qt.rgba(0.0, 0.9, 1.0, 0.6)
      border.width: 1
      radius: Math.min(width, height) * 0.15

      Label {
        text: qsTr("%1夹具%2").arg(
                fixture.edge === "top" ? qsTr("上") :
                fixture.edge === "bottom" ? qsTr("下") :
                fixture.edge === "left" ? qsTr("左") : qsTr("右"))
              .arg(fixture.index + 1)
        anchors.centerIn: parent
        color: Cores.CoreStyle.text
        font.pixelSize: 11
      }
    }
  }
}
