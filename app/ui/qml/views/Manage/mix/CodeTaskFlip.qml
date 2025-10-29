import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../../cores" as Cores
import "../../../components/Base" as BaseComponents
import "../../Task"
import "../../Code"
// Flipable container toggling between the code view and the task pipeline view.
Flipable {
  id: flipable
  property bool showingCode: true
  property bool flipped: true

  transform: Rotation {
    id: rotation
    origin.x: flipable.width/2
    origin.y: flipable.height/2
    axis.x: 0; axis.y: 1; axis.z: 0     // set axis.y to 1 to rotate around y-axis
    angle: 0    // the default angle
  }
  states: State {
    name: "back"
    PropertyChanges { target: rotation; angle: 180 }
    when: flipable.flipped
  }

  transitions: Transition {
    NumberAnimation { target: rotation; property: "angle"; duration: 600 }
  }
  front: Item {
    anchors.fill: parent
    CodeView{
      anchors.fill: parent
    }
  }

  back: Item {
    id: backSide
    anchors.fill: parent
    TaskView{
      anchors.fill: parent
    }
  }

  function toggle() {
    showingCode = !showingCode
    flipable.flipped = !flipable.flipped
  }
}
