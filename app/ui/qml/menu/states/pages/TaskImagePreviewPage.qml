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
    }
  }
}
