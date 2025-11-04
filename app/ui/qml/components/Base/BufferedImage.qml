import QtQuick

Item {
  id: root

  property url source: ""
  property int fillMode: Image.PreserveAspectFit
  property bool smooth: true
  property bool asynchronous: true
  property bool cache: false

  readonly property real paintedWidth: image.paintedWidth
  readonly property real paintedHeight: image.paintedHeight
  readonly property int status: image.status
  readonly property size sourceSize: image.sourceSize

  signal bufferStatusChanged()
  signal paintedSizeUpdated()

  implicitWidth: image.implicitWidth
  implicitHeight: image.implicitHeight

  Image {
    id: image
    anchors.fill: parent
    fillMode: root.fillMode
    smooth: root.smooth
    asynchronous: root.asynchronous
    cache: root.cache
    source: root.source
    onStatusChanged: {
      root.bufferStatusChanged()
      root.paintedSizeUpdated()
    }
    onPaintedWidthChanged: root.paintedSizeUpdated()
    onPaintedHeightChanged: root.paintedSizeUpdated()
  }
}
