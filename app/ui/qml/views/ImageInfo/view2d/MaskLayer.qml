import QtQuick

Item {
  id: maskLayer

  property url source: ""
  property bool visibleMask: false
  property real maskOpacity: 0.7
  property int fillMode: Image.Stretch
  property bool smooth: true
  property bool asynchronous: true
  property bool cache: false

  implicitWidth: maskImage.implicitWidth
  implicitHeight: maskImage.implicitHeight
  width: implicitWidth
  height: implicitHeight

  visible: maskImage.visible

  Image {
    id: maskImage
    anchors.fill: parent
    source: maskLayer.source
    fillMode: maskLayer.fillMode
    smooth: maskLayer.smooth
    asynchronous: maskLayer.asynchronous
    cache: maskLayer.cache
    opacity: maskLayer.maskOpacity
    visible: maskLayer.visibleMask && source !== ""
    layer.enabled: true
    layer.smooth: true
    layer.mipmaps: true
  }
}
