import QtQuick
import "../../Task" as TaskViews
import "../../Code" as CodeViews

// Flipable container toggling between task status overview and code viewer.
Flipable {
  id: flipable
  readonly property bool showingCode: !showingTask
  property bool showingTask: true

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
           when: !flipable.showingTask
       }
       transitions: Transition {
           NumberAnimation { target: rotation; property: "angle"; duration: 800 }
       }
     front: Item {
      id: backSide
      anchors.fill: parent
      TaskViews.TaskView {
        id: taskView
        anchors.fill: parent
        onRequestCodeView: flipable.toggle()
      }
    }
   back:Item {
    anchors.fill: parent
    CodeViews.CodeView {
      id: codeView
      anchors.fill: parent
      onRequestBack: flipable.toggle()
    }
  }



  function toggle() {
    flipable.showingTask = !flipable.showingTask
  }
}
