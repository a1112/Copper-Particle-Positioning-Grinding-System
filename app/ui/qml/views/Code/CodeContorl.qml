import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../components/btns" as Btns
import "../../cores" as Cores
import "../../datas" as Datas
import "../../Api" as Api
import "../Base"
BaseCard {
  id: root
  Layout.fillWidth: true
  implicitHeight: controlRow.implicitHeight+2

  readonly property string runState: Datas.CodeDatas.runState
  readonly property bool hasProgram: (Datas.CodeDatas.lines && Datas.CodeDatas.lines.length > 0)

  function startProgram() {
    Api.ApiClient.startRun(function() {}, function(_, err) {
      Cores.CoreError.showError(err || qsTr("启动失败"))
    })
  }

  function stopProgram() {
    Api.ApiClient.stopRun(function() {}, function(_, err) {
      Cores.CoreError.showError(err || qsTr("停止失败"))
    })
  }

  ColumnLayout {
    anchors.fill: parent

    spacing: 10

    RowLayout {
      id: controlRow
      Layout.fillWidth: true
      spacing: 12

      Label {
        text: qsTr("程序控制")
        font.bold: true
        color: Cores.CoreStyle.text
        Layout.fillWidth: true
      }

      Label {
        text: qsTr("状态: %1").arg(root.runState || "-")
        color: root.runState === "RUNNING" ? Cores.CoreStyle.success : Cores.CoreStyle.muted
      }

      Btns.ActionButton {
        text: qsTr("启动")
        enabled: root.hasProgram && root.runState !== "RUNNING"
        onClicked: startProgram()
      }

      Btns.ActionButton {
        text: qsTr("停止")
        danger: true
        enabled: root.runState === "RUNNING" || root.runState === "PAUSED"
        onClicked: stopProgram()
      }
      Btns.ActionButton {
        text: qsTr("复位")
        danger: true
        enabled: root.runState === "RUNNING" || root.runState === "PAUSED"

      }
      Btns.ActionButton {
        text: qsTr("重新执行")
        danger: true
        enabled: root.runState === "RUNNING" || root.runState === "PAUSED"

      }
    }

  }
}

