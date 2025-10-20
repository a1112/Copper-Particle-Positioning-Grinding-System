import QtQuick
import QtQuick.Controls

import "../../../cores" as Cores

Item {
  id: overlay
  anchors.fill: parent

  property int columns: 4
  property int rows: 4
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

  Repeater {
    id: fixtureRepeater
    model: Math.max(1, overlay.columns * overlay.rows)
    delegate: Rectangle {
      readonly property int col: index % overlay.columns
      readonly property int row: Math.floor(index / overlay.columns)
      readonly property real spacingX: overlay.columns > 1
                                      ? (overlay.imageWidth - overlay.marginPx * 2) / (overlay.columns - 1)
                                      : 0
      readonly property real spacingY: overlay.rows > 1
                                      ? (overlay.imageHeight - overlay.marginPx * 2) / (overlay.rows - 1)
                                      : 0
      readonly property real centerX: overlay.marginPx + col * spacingX
      readonly property real centerY: overlay.marginPx + row * spacingY

      width: overlay.fixtureWidthPx * overlay.scaleX
      height: overlay.fixtureHeightPx * overlay.scaleY
      x: centerX * overlay.scaleX - width / 2
      y: centerY * overlay.scaleY - height / 2
      color: Qt.rgba(0.15, 0.8, 0.95, 0.18)
      border.color: Qt.rgba(0.0, 0.9, 1.0, 0.6)
      border.width: 1
      radius: Math.min(width, height) * 0.15

      Label {
        text: qsTr("夹具%1").arg(index + 1)
        anchors.centerIn: parent
        color: Cores.CoreStyle.text
        font.pixelSize: 11
      }
    }
  }
}
