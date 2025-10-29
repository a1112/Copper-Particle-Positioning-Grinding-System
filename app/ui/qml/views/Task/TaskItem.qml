import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

import "../../cores" as Cores

Item {
  id: root

  signal requestCodeView()

  property var taskContext: null

  readonly property var stage: modelData
  readonly property var task: taskContext && taskContext.taskForKey ? taskContext.taskForKey(stage.key) : ({})
  readonly property bool available: taskContext && taskContext.hasTask ? taskContext.hasTask(task) : false
  readonly property bool ready: taskContext && taskContext.stageReady ? taskContext.stageReady(stage) : false
  readonly property bool showCodeSwitch: stage.key === "execute"

  Pane {
    anchors.fill: parent
    Material.elevation: 4
  }

  height: columnLayout.implicitHeight + 8

  ColumnLayout {
    id: columnLayout
    width: parent.width
    spacing: 6

    RowLayout {
      Layout.fillWidth: true
      spacing: 8

      Rectangle {
        width: 28
        height: 28
        radius: 14
        color: Cores.CoreStyle.primary

        Label {
          anchors.centerIn: parent
          text: String(index + 1)
          color: "white"
          font.bold: true
        }
      }

      ColumnLayout {
        spacing: 2

        Label {
          text: stage.title
          color: Cores.CoreStyle.text
          font.pixelSize: 18
          font.bold: true
        }

        Label {
          text: stage.subtitle
          color: Cores.CoreStyle.muted
          wrapMode: Text.WordWrap
        }
      }

      Item { Layout.fillWidth: true }

      Label {
        text: ready ? qsTr("就绪") : qsTr("等待")
        color: ready ? Cores.CoreStyle.success : Cores.CoreStyle.warning
        font.bold: true
      }

      ToolButton {
        visible: showCodeSwitch
        text: "\u2192"
        onClicked: root.requestCodeView()
      }
    }

    RowLayout {
      Layout.fillWidth: true
      spacing: 12

      Label {
        text: qsTr("任务状态")
        color: Cores.CoreStyle.muted
      }

      Label {
        text: taskContext && taskContext.statusText ? taskContext.statusText(task) : "-"
        color: taskContext && taskContext.statusColor ? taskContext.statusColor(task) : Cores.CoreStyle.muted
        font.bold: true
      }

      Item { Layout.fillWidth: true }

      Label {
        text: qsTr("任务 ID")
        color: Cores.CoreStyle.muted
      }

      Label {
        text: taskContext && taskContext.taskIdText ? taskContext.taskIdText(task) : "-"
        color: Cores.CoreStyle.text
      }

      Label {
        text: qsTr("记录")
        color: Cores.CoreStyle.muted
      }

      Label {
        text: taskContext && taskContext.recordText ? taskContext.recordText(task) : "-"
        color: Cores.CoreStyle.text
      }
    }

    RowLayout {
      Layout.fillWidth: true
      spacing: 12

      Label {
        text: qsTr("阶段")
        color: Cores.CoreStyle.muted
      }

      Label {
        text: taskContext && taskContext.phaseText ? taskContext.phaseText(task) : "-"
        color: Cores.CoreStyle.text
        Layout.fillWidth: true
        wrapMode: Text.NoWrap
        elide: Text.ElideRight
      }

      Label {
        text: qsTr("创建时间")
        color: Cores.CoreStyle.muted
      }

      Label {
        text: (available && taskContext && taskContext.timeText) ? taskContext.timeText(task, ["created_time", "createdTime", "queued_at", "queuedAt"]) : "-"
        color: Cores.CoreStyle.text
      }

      Label {
        text: qsTr("更新时间")
        color: Cores.CoreStyle.muted
      }

      Label {
        text: (available && taskContext && taskContext.timeText) ? taskContext.timeText(task, ["updated_time", "updatedTime", "finished_at", "finishedAt", "status_time", "statusTime"]) : "-"
        color: Cores.CoreStyle.text
      }
    }

    Label {
      Layout.fillWidth: true
      text: taskContext && taskContext.detailText ? taskContext.detailText(task) : "-"
      color: Cores.CoreStyle.muted
      wrapMode: Text.WordWrap
    }
  }
}
