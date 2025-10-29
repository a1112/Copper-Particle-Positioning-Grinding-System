import QtQuick
import QtQuick.Controls.Material
import QtQuick.Layouts
import "../../cores" as Cores
Item {


  readonly property var stage: modelData
  readonly property var task: taskForKey(stage.key)
  readonly property bool available: hasTask(task)
  readonly property bool ready: stageReady(stage)
  Pane{
    anchors.fill: parent
    Material.elevation: 4
  }

  height: col.height
  ColumnLayout {
    id:col
    width: parent.width
    spacing: 3
    RowLayout {
      Layout.fillWidth: true
      spacing: 2

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
    }

    RowLayout {
      Layout.fillWidth: true
      spacing: 12

      Label {
        text: qsTr("任务状态")
        color: Cores.CoreStyle.muted
      }

      Label {
        text: statusText(task)
        color: statusColor(task)
        font.bold: true
      }

      Item { Layout.fillWidth: true }

      Label {
        text: qsTr("任务 ID")
        color: Cores.CoreStyle.muted
      }

      Label {
        text: taskIdText(task)
        color: Cores.CoreStyle.text
      }

      Label {
        text: qsTr("记录")
        color: Cores.CoreStyle.muted
      }

      Label {
        text: recordText(task)
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
        text: phaseText(task)
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
        text: available ? timeText(task, ["created_time", "createdTime", "queued_at", "queuedAt"]) : "-"
        color: Cores.CoreStyle.text
      }

      Label {
        text: qsTr("更新时间")
        color: Cores.CoreStyle.muted
      }

      Label {
        text: available ? timeText(task, ["updated_time", "updatedTime", "finished_at", "finishedAt", "status_time", "statusTime"]) : "-"
        color: Cores.CoreStyle.text
      }
    }

    Label {
      Layout.fillWidth: true
      text: detailText(task)
      color: available ? Cores.CoreStyle.muted : Cores.CoreStyle.muted
      wrapMode: Text.WordWrap
    }
  }
}
