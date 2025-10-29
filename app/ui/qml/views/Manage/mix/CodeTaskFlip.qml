import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../../cores" as Cores
import "../../../components/Base" as BaseComponents

// Flipable container toggling between the code view and the task pipeline view.
Flipable {
  id: flipable
  property bool showingCode: true
  property bool flipped: false

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
    ColumnLayout {
      anchors.fill: parent
      spacing: 8

      RowLayout {
        Layout.fillWidth: true
        spacing: 8

        Label {
          text: qsTr("代码视图")
          font.pixelSize: 18
          font.bold: true
          color: Cores.CoreStyle.text
        }

        Item { Layout.fillWidth: true }

        BaseComponents.ItemDelegateBase {
          text: qsTr("查看任务流程")
          onClicked: flipable.toggle()
        }
      }

      Loader {
        id: codeLoader
        Layout.fillWidth: true
        Layout.fillHeight: true
        asynchronous: true
        source: Qt.resolvedUrl("../../Code/CodeView.qml")
      }
    }
  }

  back: Item {
    id: backSide
    anchors.fill: parent
    ColumnLayout {
      anchors.fill: parent
      spacing: 1
      RowLayout {
        Layout.fillWidth: true
        spacing: 2
        Label {
          text: qsTr("任务流程")
          font.pixelSize: 18
          font.bold: true
          color: Cores.CoreStyle.text
        }
        Item{
          Layout.fillWidth: true
        }
        BaseComponents.ItemDelegateBase {
          text: qsTr("返回代码")
          onClicked: flipable.toggle()
        }
      }
      Loader {
        id: taskLoader
        Layout.fillWidth: true
        Layout.fillHeight: true
        asynchronous: true
        source: Qt.resolvedUrl("../../Task/TaskView.qml")
      }
    }
  }

  function toggle() {
    showingCode = !showingCode
    flipable.flipped = !flipable.flipped
  }
}
