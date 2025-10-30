import QtQuick
import QtQuick3D

Node {
  id: root

  property url meshSource: ""
  property string fallbackPrimitive: "#Cube"
  property color baseColor: "#f3f4f6"
  property bool reloadOnSourceChange: true
  property string errorString: ""
  property int modelStatus: (model.status !== undefined ? model.status : statusNull)
  readonly property int statusNull: 0
  readonly property int statusReady: 1
  readonly property int statusError: 2
  readonly property int statusLoading: 3

  onMeshSourceChanged: {
    if (!reloadOnSourceChange)
      return
    reloadTimer.restart()
  }

  Timer {
    id: reloadTimer
    interval: 80
    repeat: false
    onTriggered: {
      if (!root.meshSource) {
        model.source = root.fallbackPrimitive
      } else if (String(root.meshSource).length === 0) {
        model.source = root.fallbackPrimitive
      } else {
        model.source = ""
        resetTimer.restart()
      }
    }
  }

  Timer {
    id: resetTimer
    interval: 20
    repeat: false
    onTriggered: model.source = root.meshSource
  }

  signal modelBoundsReady(var minBounds, var maxBounds)

  onModelStatusChanged: {
    if (modelStatus === statusError) {
      errorString = qsTr("模型加载失败")
      if (model.source !== root.fallbackPrimitive)
        model.source = root.fallbackPrimitive
    } else if (modelStatus === statusReady) {
      errorString = ""
      var bounds = model.bounds
      if (bounds && bounds.minimum && bounds.maximum)
        modelBoundsReady(bounds.minimum, bounds.maximum)
    } else if (modelStatus === statusLoading) {
      errorString = ""
    }
  }

  Model {
    id: model
    source: root.fallbackPrimitive
    materials: [
      PrincipledMaterial {
        id: defaultMaterial
        baseColor: root.baseColor
        roughness: 0.35
        metalness: 0.0
      }
    ]
  }
}
