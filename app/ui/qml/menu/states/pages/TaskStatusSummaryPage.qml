import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../../cores" as Cores
import "../../../datas" as Datas

ScrollView {
  id: root
  required property var statePageCore

  Layout.fillWidth: true
  Layout.fillHeight: true

  clip: true
  ScrollBar.vertical.policy: ScrollBar.AsNeeded

  contentItem: Flickable {
    id: commandFlick
    clip: true
    contentWidth: width
    contentHeight: commandColumn.implicitHeight
    boundsBehavior: Flickable.StopAtBounds

    ColumnLayout {
      id: commandColumn
      width: commandFlick.width - 12
      spacing: 20

      ColumnLayout {
        Layout.fillWidth: true
        spacing: 12

        Label {
          text: Datas.TaskDatas.alarmLocked ? qsTr("控制已锁定，请先在报警页复位。") : ""
          color: Datas.TaskDatas.alarmLocked ? Cores.CoreStyle.danger : Cores.CoreStyle.muted
          visible: Datas.TaskDatas.alarmLocked
          wrapMode: Text.Wrap
        }

        Label {
          text: qsTr("任务队列")
          font.pixelSize: 18
          font.bold: true
          color: Cores.CoreStyle.text
        }

        Repeater {
          model: [
            ({ title: qsTr("采集任务"), task: statePageCore.captureTask, ready: Datas.TaskDatas.captureReady }),
            ({ title: qsTr("执行任务"), task: statePageCore.executeTask, ready: Datas.TaskDatas.executeReady }),
            ({ title: qsTr("控制任务"), task: statePageCore.controlTask, ready: Datas.TaskDatas.controlReady })
          ]

          delegate: ColumnLayout {
            Layout.fillWidth: true
            spacing: 6

            Label {
              text: modelData.title + " · " + (modelData.ready ? qsTr("就绪") : qsTr("等待"))
              font.pixelSize: 16
              font.bold: true
              color: modelData.ready ? Cores.CoreStyle.success : Cores.CoreStyle.warning
            }

            Rectangle {
              Layout.fillWidth: true
              radius: 8
              color: "#111a28"
              border.color: "#1d2a3f"

              ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 10

                RowLayout {
                  Layout.fillWidth: true
                  spacing: 18
                  Label { text: qsTr("状态"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 80 }
                  Label {
                    text: statePageCore.taskStatusText(modelData.task.status)
                    color: statePageCore.statusColor(modelData.task.status)
                    font.pixelSize: 15
                    font.bold: true
                  }
                  Label { text: qsTr("阶段"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 80 }
                  Label {
                    text: statePageCore.phaseText(modelData.task)
                    color: Cores.CoreStyle.text
                    Layout.fillWidth: true
                  }
                }

                RowLayout {
                  Layout.fillWidth: true
                  spacing: 18
                  Label { text: qsTr("创建时间"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 80 }
                  Label {
                    text: statePageCore.formatTimestamp(modelData.task.created_time || modelData.task.createdTime)
                    color: Cores.CoreStyle.text
                    Layout.fillWidth: true
                  }
                  Label { text: qsTr("更新"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 60 }
                  Label {
                    text: statePageCore.formatTimestamp(modelData.task.updated_time || modelData.task.updatedTime)
                    color: Cores.CoreStyle.text
                    Layout.fillWidth: true
                  }
                }

                Label {
                  text: statePageCore.detailText(modelData.task)
                  color: Cores.CoreStyle.muted
                  wrapMode: Text.Wrap
                }
              }
            }
          }
        }
      }
    }
  }
}
