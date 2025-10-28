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
          text: Datas.TaskDatas.alarmLocked ? qsTr("\u63A7\u5236\u5DF2\u9501\u5B9A\uFF0C\u8BF7\u5148\u5728\u62A5\u8B66\u9875\u590D\u4F4D\u3002") : ""
          color: Datas.TaskDatas.alarmLocked ? Cores.CoreStyle.danger : Cores.CoreStyle.muted
          visible: Datas.TaskDatas.alarmLocked
          wrapMode: Text.Wrap
        }

        Label {
          text: qsTr("\u4EFB\u52A1\u961F\u5217")
          font.pixelSize: 18
          font.bold: true
          color: Cores.CoreStyle.text
        }

        Repeater {
          model: [
            ({ title: qsTr("\u91C7\u96C6\u4EFB\u52A1"), task: statePageCore.captureTask, ready: Datas.TaskDatas.captureReady }),
            ({ title: qsTr("\u6267\u884C\u4EFB\u52A1"), task: statePageCore.executeTask, ready: Datas.TaskDatas.executeReady }),
            ({ title: qsTr("\u63A7\u5236\u4EFB\u52A1"), task: statePageCore.controlTask, ready: Datas.TaskDatas.controlReady })
          ]

          delegate: ColumnLayout {
            Layout.fillWidth: true
            spacing: 6

            Label {
              text: modelData.title + " \u00B7 " + (modelData.ready ? qsTr("\u5C31\u7EEA") : qsTr("\u7B49\u5F85"))
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
                  Label { text: qsTr("\u72B6\u6001"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 80 }
                  Label {
                    text: statePageCore.taskStatusText(modelData.task.status)
                    color: statePageCore.statusColor(modelData.task.status)
                    font.pixelSize: 15
                    font.bold: true
                  }
                  Label { text: qsTr("\u9636\u6BB5"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 80 }
                  Label {
                    text: statePageCore.phaseText(modelData.task)
                    color: Cores.CoreStyle.text
                    Layout.fillWidth: true
                  }
                }

                RowLayout {
                  Layout.fillWidth: true
                  spacing: 18
                  Label { text: qsTr("\u521B\u5EFA\u65F6\u95F4"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 80 }
                  Label {
                    text: statePageCore.formatTimestamp(modelData.task.created_time || modelData.task.createdTime)
                    color: Cores.CoreStyle.text
                    Layout.fillWidth: true
                  }
                  Label { text: qsTr("\u66F4\u65B0"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 60 }
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
