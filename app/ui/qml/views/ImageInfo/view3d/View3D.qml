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
  property bool showRobotArm: false  // 显示机器人模型
  property alias loadStatus: modelNode.modelStatus
  property string errorString: ""

  // 机器人关节角度
  property int robotRotation1: 0
  property int robotRotation2: 45
  property int robotRotation3: 45
  property int robotRotation4: 0
  property int robotClawsAngle: 0

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

      // 机器人模型节点
      RoboticArm {
        id: roboticArm
        visible: root.showRobotArm
        rotation1: root.robotRotation1
        rotation2: root.robotRotation2
        rotation3: root.robotRotation3
        rotation4: root.robotRotation4
        clawsAngle: root.robotClawsAngle
        // 机器人位置和旋转调整
        y: -100
        eulerRotation.z: -90
      }

      // 普通模型节点
      ModelNode3D {
        id: modelNode
        visible: !root.showRobotArm
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
  }

  Control3D {
    core3D: core3D
    showOverlay: root.showControls
  }

  // 机器人控制面板
  RobotControlPanel {
    id: robotControl
    visible: root.showRobotArm && root.showControls
    anchors.left: parent.left
    anchors.top: parent.top
    anchors.margins: 12

    rotation1Value: root.robotRotation1
    rotation2Value: root.robotRotation2
    rotation3Value: root.robotRotation3
    rotation4Value: root.robotRotation4
    clawsOpen: root.robotClawsAngle === 0

    onRotation1Changed: root.robotRotation1 = value
    onRotation2Changed: root.robotRotation2 = value
    onRotation3Changed: root.robotRotation3 = value
    onRotation4Changed: root.robotRotation4 = value
    onClawsToggled: root.robotClawsAngle = open ? 0 : 90
    onResetClicked: {
      root.robotRotation1 = 0
      root.robotRotation2 = 45
      root.robotRotation3 = 45
      root.robotRotation4 = 0
      root.robotClawsAngle = 0
    }
  }

  LabelLayer {

  }
}
