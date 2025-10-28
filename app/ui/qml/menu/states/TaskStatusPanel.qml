import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../cores" as Cores
import "../../datas" as Datas
import "../../works" as Works

Item {
  id: root
  required property var statePageCore

  Layout.fillWidth: true
  Layout.fillHeight: true

  ScrollView {
    anchors.fill: parent
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

        ColumnLayout {
          Layout.fillWidth: true
          spacing: 10

          RowLayout {
            Layout.fillWidth: true
            spacing: 10
            Label {
              text: qsTr("任务指令列表")
              font.pixelSize: 18
              font.bold: true
              color: Cores.CoreStyle.text
            }
            Item { Layout.fillWidth: true }
            Button {
              text: qsTr("清空指令")
              enabled: statePageCore.commandModel.length > 0 && Datas.StatusDatas.controlEnabled && !Datas.TaskDatas.alarmLocked
              onClicked: Works.TaskWork.clearCommands()
            }
            Label {
              text: statePageCore.commandModel.length ? qsTr("共 %1 条").arg(statePageCore.commandModel.length) : qsTr("暂无指令")
              color: Cores.CoreStyle.muted
            }
          }

          Rectangle {
            Layout.fillWidth: true
            radius: 6
            color: "#172033"
            border.color: "#1f2c44"
            height: headerRow.implicitHeight + 12

            RowLayout {
              id: headerRow
              anchors.fill: parent
              anchors.margins: 8
              spacing: 12
              Label { text: qsTr("序号"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 60 }
              Label { text: qsTr("指令"); color: Cores.CoreStyle.muted; Layout.fillWidth: true }
              Label { text: qsTr("位移 (mm)"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 140 }
              Label { text: qsTr("转速"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 90 }
              Label { text: qsTr("进给"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 90 }
              Label { text: qsTr("状态"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 100 }
              Label { text: qsTr("时间"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 160 }
              Label { text: qsTr("备注"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 180 }
              Label { text: qsTr("操作"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 80 }
            }
          }

          Repeater {
            model: statePageCore.commandModel
            delegate: Rectangle {
              Layout.fillWidth: true
              radius: 4
              color: index % 2 === 0 ? "#101725" : "#0d1421"
              border.color: "#182133"
              height: contentRow.implicitHeight + 10

              RowLayout {
                id: contentRow
                anchors.fill: parent
                anchors.margins: 8
                spacing: 12

                Label { text: modelData.sequence; color: Cores.CoreStyle.text; Layout.preferredWidth: 60 }
                Label {
                  text: modelData.commandText
                  color: Cores.CoreStyle.text
                  wrapMode: Text.Wrap
                  Layout.fillWidth: true
                }
                Label {
                  text: statePageCore.displacementText(modelData)
                  color: Cores.CoreStyle.text
                  Layout.preferredWidth: 140
                  wrapMode: Text.Wrap
                }
                Label {
                  text: modelData.rpm !== undefined ? modelData.rpm.toFixed(1) : "-"
                  color: Cores.CoreStyle.text
                  Layout.preferredWidth: 90
                }
                Label {
                  text: modelData.velocity !== undefined ? modelData.velocity.toFixed(2) : "-"
                  color: Cores.CoreStyle.text
                  Layout.preferredWidth: 90
                }
                Label {
                  text: modelData.statusText
                  color: modelData.statusTone
                  font.bold: true
                  Layout.preferredWidth: 100
                }
                Label {
                  text: modelData.timestamp
                  color: Cores.CoreStyle.muted
                  Layout.preferredWidth: 160
                  wrapMode: Text.WrapAnywhere
                }
                Label {
                  text: modelData.message ? modelData.message : modelData.source
                  color: Cores.CoreStyle.muted
                  wrapMode: Text.Wrap
                  Layout.preferredWidth: 180
                }
                Button {
                  text: qsTr("删除")
                  enabled: Datas.StatusDatas.controlEnabled && !Datas.TaskDatas.alarmLocked && modelData && modelData.id
                  Layout.preferredWidth: 80
                  onClicked: Works.TaskWork.deleteCommand(modelData.id)
                }
              }
            }
          }

          Label {
            visible: statePageCore.commandModel.length === 0
            text: qsTr("当前流水号暂无控制指令，请等待采集任务完成后再试。")
            color: Cores.CoreStyle.muted
          }
        }

        ColumnLayout {
          Layout.fillWidth: true
          spacing: 10

          RowLayout {
            Layout.fillWidth: true
            spacing: 10
            Label {
              text: qsTr("采集图像预览")
              font.pixelSize: 18
              font.bold: true
              color: Cores.CoreStyle.text
            }
            Item { Layout.fillWidth: true }
            Label {
              text: Datas.TaskDatas.latestRecordId ? qsTr("记录 #%1").arg(Datas.TaskDatas.latestRecordId) : "-"
              color: Cores.CoreStyle.muted
            }
          }

          Flow {
            Layout.fillWidth: true
            spacing: 14

            Repeater {
              model: statePageCore.imageModel
              delegate: ColumnLayout {
                width: Math.min(260, commandColumn.width / 3)
                spacing: 6

                Rectangle {
                  Layout.fillWidth: true
                  height: width * 0.75
                  radius: 8
                  color: "#0f1722"
                  border.color: "#1c2840"
                  clip: true

                  Image {
                    anchors.fill: parent
                    fillMode: Image.PreserveAspectFit
                    source: modelData.url
                  }
                }

                Label {
                  text: modelData.title
                  color: Cores.CoreStyle.text
                  font.bold: true
                }

                Label {
                  text: modelData.path
                  color: Cores.CoreStyle.muted
                  wrapMode: Text.WrapAnywhere
                }
              }
            }

            Label {
              visible: statePageCore.imageModel.length === 0
              text: qsTr("暂无采集图像，请先完成采集流程。")
              color: Cores.CoreStyle.muted
            }
          }
        }

        ColumnLayout {
          Layout.fillWidth: true
          spacing: 8

          RowLayout {
            Layout.fillWidth: true
            spacing: 10
            Label {
              text: qsTr("路径预览")
              font.pixelSize: 18
              font.bold: true
              color: Cores.CoreStyle.text
            }
            Item { Layout.fillWidth: true }
            Label {
              text: statePageCore.pathModel.length ? qsTr("共 %1 段").arg(statePageCore.pathModel.length) : ""
              color: Cores.CoreStyle.muted
            }
          }

          Rectangle {
            Layout.fillWidth: true
            radius: 6
            color: "#141d2e"
            border.color: "#1f2c44"

            ColumnLayout {
              anchors.fill: parent
              anchors.margins: 12
              spacing: 6

              Repeater {
                model: statePageCore.pathModel
                delegate: RowLayout {
                  Layout.fillWidth: true
                  spacing: 12

                  Label {
                    text: modelData.indexText
                    color: Cores.CoreStyle.info
                    font.bold: true
                    Layout.preferredWidth: 40
                  }
                  Label {
                    text: modelData.command
                    color: Cores.CoreStyle.text
                    Layout.fillWidth: true
                    wrapMode: Text.Wrap
                  }
                  Label {
                    text: modelData.positionText
                    color: Cores.CoreStyle.muted
                    Layout.preferredWidth: 220
                    wrapMode: Text.WrapAnywhere
                  }
                  Label {
                    text: modelData.velocityText
                    color: Cores.CoreStyle.muted
                    Layout.preferredWidth: 80
                  }
                }
              }

              Label {
                visible: statePageCore.pathModel.length === 0
                text: qsTr("暂无路径信息，等待采集完成生成。")
                color: Cores.CoreStyle.muted
              }
            }
          }
        }
      }
    }
  }
}
