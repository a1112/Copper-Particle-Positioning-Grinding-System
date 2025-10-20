import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../../cores" as Cores

Item {
  id: root
  property Item core3D
  property bool allowRotate: true
  property bool allowPan: true
  property bool showOverlay: true

  anchors.fill: parent
  HoverHandler { acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad }

  WheelHandler {
    id: wheelHandler
    target: root
    onWheel: {
      if (!root.core3D)
        return
      root.core3D.adjustZoom(wheel.angleDelta.y)
      wheel.accepted = true
    }
  }

  MouseArea {
    anchors.fill: parent
    acceptedButtons: Qt.LeftButton | Qt.RightButton
    preventStealing: true
    onPressed: function(mouse) {
      if (!root.core3D)
        return
      if (mouse.button === Qt.LeftButton && root.allowRotate)
        root.core3D.beginRotate(mouse.x, mouse.y)
      else if (mouse.button === Qt.RightButton && root.allowPan)
        root.core3D.beginPan(mouse.x, mouse.y)
    }
    onPositionChanged: function(mouse) {
      if (!root.core3D)
        return
      if ((mouse.buttons & Qt.LeftButton) && root.allowRotate)
        root.core3D.rotateTo(mouse.x, mouse.y)
      if ((mouse.buttons & Qt.RightButton) && root.allowPan)
        root.core3D.panTo(mouse.x, mouse.y)
    }
  }

  RowLayout {
    id: controlsRow
    anchors.top: parent.top
    anchors.right: parent.right
    anchors.margins: 12
    spacing: 8
    visible: root.showOverlay && root.core3D

    Label {
      text: qsTr("缩放")
      color: Cores.CoreStyle.text
      font.pixelSize: 12
      opacity: 0.7
    }

    Slider {
      id: scaleSlider
      Layout.preferredWidth: 120
      from: 0.2
      to: 3.5
      stepSize: 0.1
      value: root.core3D ? root.core3D.objectScale.x : 1
      onMoved: {
        if (!root.core3D)
          return
        var s = Qt.vector3d(value, value, value)
        root.core3D.objectScale = s
      }
    }

    Label {
      text: scaleSlider.value.toFixed(1) + "x"
      color: Cores.CoreStyle.muted
      font.pixelSize: 12
    }

    ToolButton {
      text: qsTr("重置")
      onClicked: root.core3D && root.core3D.resetView()
      ToolTip.visible: hovered
      ToolTip.text: qsTr("重置视角")
    }
  }
}
