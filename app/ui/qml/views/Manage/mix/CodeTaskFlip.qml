import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../cores" as Cores
import "../../components/Base" as BaseComponents

// Flipable container toggling between the code view and the task pipeline view.
Flipable {
  id: root
  property bool showingCode: true

  implicitWidth: 960
  implicitHeight: 540
  transformOrigin: Item.Center

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
          onClicked: root.toggle()
        }
      }

      Loader {
        id: codeLoader
        Layout.fillWidth: true
        Layout.fillHeight: true
        asynchronous: true
        source: Qt.resolvedUrl("../../Code/CodeView.qml")
        onLoaded: if (item && item.anchors) item.anchors.fill = parent
      }
    }
  }

  back: Item {
    anchors.fill: parent
    rotationY: 180

    ColumnLayout {
      anchors.fill: parent
      spacing: 8

      RowLayout {
        Layout.fillWidth: true
        spacing: 8

        Label {
          text: qsTr("任务流程")
          font.pixelSize: 18
          font.bold: true
          color: Cores.CoreStyle.text
        }

        Item { Layout.fillWidth: true }

        BaseComponents.ItemDelegateBase {
          text: qsTr("返回代码")
          onClicked: root.toggle()
        }
      }

      Loader {
        id: taskLoader
        Layout.fillWidth: true
        Layout.fillHeight: true
        asynchronous: true
        source: Qt.resolvedUrl("../../Task/TaskView.qml")
        onLoaded: if (item && item.anchors) item.anchors.fill = parent
      }
    }
  }

  function toggle() {
    showingCode = !showingCode
    root.state = showingCode ? "" : "flipped"
  }

  states: [
    State {
      name: "flipped"
      PropertyChanges { target: root; rotationY: 180 }
    }
  ]

  transitions: Transition {
    NumberAnimation { properties: "rotationY"; duration: 320; easing.type: Easing.InOutQuad }
  }

  onShowingCodeChanged: root.state = showingCode ? "" : "flipped"

  Component.onCompleted: root.state = showingCode ? "" : "flipped"
}
