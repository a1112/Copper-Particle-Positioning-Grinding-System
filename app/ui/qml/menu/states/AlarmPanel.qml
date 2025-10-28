import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../cores" as Cores
import "../../datas" as Datas

Item {
  id: root
  required property var statePageCore

  Layout.fillWidth: true
  Layout.fillHeight: true

  ColumnLayout {
    anchors.fill: parent
    spacing: 14

    RowLayout {
      Layout.fillWidth: true
      Label {
        text: qsTr("报警列表")
        font.pixelSize: 18
        font.bold: true
        color: Cores.CoreStyle.text
      }
      Item { Layout.fillWidth: true }
      Label {
        text: statePageCore.alarmModel.length ? qsTr("最大等级: %1").arg(statePageCore.alarmModel[0].levelText) : ""
        color: statePageCore.alarmModel.length ? statePageCore.alarmModel[0].tone : Cores.CoreStyle.muted
        visible: statePageCore.alarmModel.length > 0
      }
      Button {
        text: statePageCore.resetting ? qsTr("复位中...") : qsTr("复位报警")
        enabled: !statePageCore.resetting
        onClicked: statePageCore.resetAlarms()
      }
    }

    ScrollView {
      Layout.fillWidth: true
      Layout.fillHeight: true
      clip: true
      ScrollBar.vertical.policy: ScrollBar.AsNeeded

      contentItem: Flickable {
        id: alertFlick
        clip: true
        contentHeight: alertColumn.implicitHeight
        contentWidth: width
        boundsBehavior: Flickable.StopAtBounds

        ColumnLayout {
          id: alertColumn
          width: alertFlick.width - 12
          spacing: 12

          Repeater {
            model: statePageCore.alarmModel
            delegate: Rectangle {
              Layout.fillWidth: true
              radius: 8
              color: "#131a27"
              border.color: "#1d2535"

              ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 6

                RowLayout {
                  Layout.fillWidth: true
                  spacing: 10
                  Rectangle {
                    width: 10
                    height: 10
                    radius: 5
                    color: modelData.tone
                    border.color: modelData.tone
                  }
                  Label {
                    text: modelData.levelText
                    font.bold: true
                    color: modelData.tone
                  }
                  Label {
                    text: modelData.code && modelData.code !== "-" ? ("#" + modelData.code) : ""
                    color: Cores.CoreStyle.muted
                  }
                  Label {
                    text: modelData.statusText
                    color: modelData.statusTone
                  }
                  Item { Layout.fillWidth: true }
                  Label {
                    text: modelData.timestamp
                    color: Cores.CoreStyle.muted
                  }
                }

                Label {
                  text: modelData.message
                  color: Cores.CoreStyle.text
                  wrapMode: Text.Wrap
                }

                Label {
                  text: modelData.source ? qsTr("来源: %1").arg(modelData.source) : ""
                  color: Cores.CoreStyle.muted
                  visible: modelData.source && modelData.source.length > 0
                }

                Label {
                  text: modelData.handler && modelData.handler.length > 0 ? qsTr("处理人: %1").arg(modelData.handler) : ""
                  color: Cores.CoreStyle.muted
                  visible: modelData.handler && modelData.handler.length > 0
                }
              }
            }
          }

          Label {
            visible: statePageCore.alarmModel.length === 0
            text: qsTr("当前无报警，设备运行正常。")
            color: Cores.CoreStyle.muted
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
          }
        }
      }
    }

    Label {
      text: statePageCore.actionMessage
      color: Cores.CoreStyle.info
      visible: statePageCore.actionMessage.length > 0
    }
  }
}



