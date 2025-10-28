import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../../cores" as Cores
import "../../../datas" as Datas
import "../../../works" as Works

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
            text: qsTr("命令列表")
            font.pixelSize: 18
            font.bold: true
            color: Cores.CoreStyle.text
          }
          Item { Layout.fillWidth: true }
          Button {
            text: qsTr("清空命令")
            enabled: statePageCore.commandModel.length > 0 && Datas.StatusDatas.controlEnabled && !Datas.TaskDatas.alarmLocked
            onClicked: Works.TaskWork.clearCommands()
          }
          Label {
            text: statePageCore.commandModel.length ? qsTr("共 %1 条").arg(statePageCore.commandModel.length) : qsTr("无命令")
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
            Label { text: qsTr("速度"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 90 }
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
          text: qsTr("当前流水线暂无控制指令，待采集完成后可用。")
          color: Cores.CoreStyle.muted
        }
      }
    }
  }
}
