import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick3D
import QtQuick3D.Helpers

import "../../../cores" as Cores
import "layer"
Item {
  id: root
  Layout.fillWidth: true
  Layout.fillHeight: true

  property url meshSource: ""
  property color modelColor: "#f3f4f6"
  property bool showControls: true
  property bool showGrid: true
  property bool autoCenter: true
  property alias loadStatus: modelNode.modelStatus
  property string errorString: ""

  readonly property bool isLoading: loadStatus === modelNode.statusLoading
  readonly property bool hasError: loadStatus === modelNode.statusError

  Core3D {
    id: core3D
  }

  Rectangle {
    anchors.fill: parent
    radius: 4
    color: Cores.CoreStyle.surface
    border.color: Cores.CoreStyle.border
    border.width: 1
  }

  View3D {
    id: viewport
    anchors.fill: parent
    renderMode: View3D.Offscreen
    environment: SceneEnvironment {
      id: env
      backgroundMode: SceneEnvironment.Color
      clearColor: Qt.rgba(0.05, 0.08, 0.12, 1)
      lightProbe: Texture {
        textureData: ProceduralSkyTextureData { sunLongitude: 30; sunLatitude: 25 }
      }
      InfiniteGrid {
        visible: root.showGrid
        gridInterval: 250

      }
    }

    Node {
      id: sceneRoot

      DirectionalLight {
        eulerRotation: Qt.vector3d(-45, -45, 0)
        brightness: 2500
        castsShadow: true
      }

      DirectionalLight {
        eulerRotation: Qt.vector3d(65, 120, 0)
        brightness: 1200
        shadowFactor: 0.2
      }

      PerspectiveCamera {
        id: sceneCamera
        x: core3D.cameraOffsetX
        y: core3D.cameraOffsetY
        z: core3D.cameraOffsetZ
        clipFar: 200000
        clipNear: 10
      }
    }

    ModelNode3D {
      id: modelNode
      meshSource: root.meshSource
      baseColor: root.modelColor
      eulerRotation.x: core3D.objectRotationX
      eulerRotation.y: core3D.objectRotationY
      eulerRotation.z: core3D.objectRotationZ
      x: core3D.objectOffsetX
      y: core3D.objectOffsetY
      z: core3D.objectOffsetZ
      scale: core3D.objectScale
      onErrorStringChanged: root.errorString = errorString
      onModelBoundsReady: function(minBounds, maxBounds) {
        if (root.autoCenter)
          core3D.applyAutoCenter(minBounds, maxBounds)
      }
    }

  }

  Control3D {
    core3D: core3D
    showOverlay: root.showControls
  }


  LabelLayer{

  }
}
