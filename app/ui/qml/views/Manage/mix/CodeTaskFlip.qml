import QtQuick
import "../../Task" as TaskViews
import "../../Code" as CodeViews

// Flipable container toggling between task status overview and code viewer.
Flipable {
  id: flipable
  property bool showingCode: false

  readonly property bool showingTask: !showingCode
  states: State {
           name: "back"
           PropertyChanges { target: rotation; angle: 180 }
           when: flipable.flipped
       }

       transitions: Transition {
           NumberAnimation { target: rotation; property: "angle"; duration: 4000 }
       }
  transform: Rotation {
    origin.x: flipable.width / 2
    origin.y: flipable.height / 2
    axis.y: 1
    angle: flipable.showingCode ? 0 : 180
    Behavior on angle { NumberAnimation { duration: 400; easing.type: Easing.InOutQuad } }
  }

  front: Item {
    anchors.fill: parent

    CodeViews.CodeView {
      id: codeView
      anchors.fill: parent
      onRequestBack: flipable.showTask()
    }
  }

  back: Item {
    id: backSide
    anchors.fill: parent

    TaskViews.TaskView {
      id: taskView
      anchors.fill: parent
      onRequestCodeView: flipable.showCode()
    }
  }

  function showTask() {
    if (!flipable.showingCode)
      return
    flipable.showingCode = false
  }

  function showCode() {
    if (flipable.showingCode)
      return
    flipable.showingCode = true
  }

  function toggle() {
    flipable.showingCode = !flipable.showingCode
  }
}
