import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../../cores" as Cores

ScrollView {
  id: root
  required property var statePageCore

  Layout.fillWidth: true
  Layout.fillHeight: true
  clip: true
  ScrollBar.vertical.policy: ScrollBar.AsNeeded

  contentItem: Flickable {
    id: commandFlick
    width: parent.width
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
        spacing: 2

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


          ColumnLayout {
            id:col
            Layout.fillWidth: true
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
