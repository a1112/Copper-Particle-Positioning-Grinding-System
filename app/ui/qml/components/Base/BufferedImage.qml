import QtQuick

Item {
  id: root

  property url source: ""
  property int fillMode: Image.PreserveAspectFit
  property bool smooth: true
  property bool asynchronous: true
  property bool cache: false

  readonly property real paintedWidth: activeBuffer === 0 ? imgBuffer0.paintedWidth : imgBuffer1.paintedWidth
  readonly property real paintedHeight: activeBuffer === 0 ? imgBuffer0.paintedHeight : imgBuffer1.paintedHeight
  readonly property int status: activeBuffer === 0 ? imgBuffer0.status : imgBuffer1.status

  signal statusChanged()
  signal paintedSizeChanged()

  property int activeBuffer: 0
  property int pendingBuffer: -1
  property url bufferSource0: ""
  property url bufferSource1: ""

  implicitWidth: Math.max(imgBuffer0.implicitWidth, imgBuffer1.implicitWidth)
  implicitHeight: Math.max(imgBuffer0.implicitHeight, imgBuffer1.implicitHeight)

  function requestImageRefresh(url) {
    if (!url) {
      bufferSource0 = ""
      bufferSource1 = ""
      pendingBuffer = -1
      activeBuffer = 0
      statusChanged()
      paintedSizeChanged()
      return
    }
    var targetBuffer
    if (bufferSource0 === "" && bufferSource1 === "")
      targetBuffer = activeBuffer
    else if (pendingBuffer >= 0)
      targetBuffer = pendingBuffer
    else
      targetBuffer = activeBuffer === 0 ? 1 : 0
    pendingBuffer = targetBuffer
    if (targetBuffer === 0) {
      bufferSource0 = ""
      bufferSource0 = url
    } else {
      bufferSource1 = ""
      bufferSource1 = url
    }
  }

  function handleBufferReady(index) {
    if (pendingBuffer === index || (pendingBuffer === -1 && activeBuffer !== index)) {
      activeBuffer = index
      pendingBuffer = -1
      statusChanged()
      paintedSizeChanged()
    }
  }

  onActiveBufferChanged: paintedSizeChanged()
  onSourceChanged: requestImageRefresh(source)

  Image {
    id: imgBuffer0
    anchors.fill: parent
    fillMode: root.fillMode
    smooth: root.smooth
    asynchronous: root.asynchronous
    cache: root.cache
    source: root.bufferSource0
    visible: root.activeBuffer === 0
    z: root.activeBuffer === 0 ? 1 : 0
    onStatusChanged: {
      if (status === Image.Ready)
        root.handleBufferReady(0)
      else if (status === Image.Error && root.pendingBuffer === 0)
        root.pendingBuffer = -1
      root.statusChanged()
    }
    onPaintedWidthChanged: root.paintedSizeChanged()
    onPaintedHeightChanged: root.paintedSizeChanged()
  }

  Image {
    id: imgBuffer1
    anchors.fill: parent
    fillMode: root.fillMode
    smooth: root.smooth
    asynchronous: root.asynchronous
    cache: root.cache
    source: root.bufferSource1
    visible: root.activeBuffer === 1
    z: root.activeBuffer === 1 ? 1 : 0
    onStatusChanged: {
      if (status === Image.Ready)
        root.handleBufferReady(1)
      else if (status === Image.Error && root.pendingBuffer === 1)
        root.pendingBuffer = -1
      root.statusChanged()
    }
    onPaintedWidthChanged: root.paintedSizeChanged()
    onPaintedHeightChanged: root.paintedSizeChanged()
  }

  Connections {
    target: Qt.application
    function onAboutToQuit() {
      bufferSource0 = ""
      bufferSource1 = ""
    }
  }

  Component.onCompleted: requestImageRefresh(source)
}
