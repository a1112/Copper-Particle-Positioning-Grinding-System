import QtQuick

Item {
  id: layer

  property url source: ""
  property int fillMode: Image.Stretch
  property bool smooth: true
  property bool asynchronous: true
  property bool cache: false
  property real contentOpacity: 1.0

  signal paintedSizeUpdated()
  signal statusChanged(int status)

  implicitWidth: image.implicitWidth
  implicitHeight: image.implicitHeight
  width: implicitWidth
  height: implicitHeight

  readonly property alias paintedWidth: image.paintedWidth
  readonly property alias paintedHeight: image.paintedHeight
  readonly property alias sourceSize: image.sourceSize
  readonly property alias status: image.status

  Image {
    id: image
    anchors.fill: parent
    source: layer.source
    fillMode: layer.fillMode
    smooth: layer.smooth
    asynchronous: layer.asynchronous
    cache: layer.cache
    opacity: layer.contentOpacity
    layer.enabled: true
    layer.smooth: true
    layer.mipmaps: true
    onStatusChanged: {
      layer.statusChanged(status)
      layer.paintedSizeUpdated()
    }
    onPaintedWidthChanged: layer.paintedSizeUpdated()
    onPaintedHeightChanged: layer.paintedSizeUpdated()
  }
}
