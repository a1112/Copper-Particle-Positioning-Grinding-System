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
  implicitHeight: controlRow.implicitHeight + 2

  readonly property string runState: Datas.CodeDatas.runState
  readonly property bool hasProgram: Array.isArray(Datas.CodeDatas.lines) && Datas.CodeDatas.lines.length > 0

  function resolvedRunState() {
    var stateValue = root.runState
    if (stateValue === undefined)
      return "-"
    if (stateValue === null)
      return "-"
    if (stateValue === "")
      return "-"
    return stateValue
  }

  function fallbackMessage(value, defaultText) {
    if (value === undefined)
      return defaultText
    if (value === null)
      return defaultText
    if (value === "")
      return defaultText
    return value
  }

  function startProgram() {
    Api.ApiClient.startRun(
      function() {},
      function(_, err) { Cores.CoreError.showError(fallbackMessage(err, qsTr("启动失败"))) }
    )
  }

  function stopProgram() {
    Api.ApiClient.stopRun(
      function() {},
      function(_, err) { Cores.CoreError.showError(fallbackMessage(err, qsTr("停止失败"))) }
    )
  }

  function isRunningOrPaused() {
    return ["RUNNING", "PAUSED"].indexOf(root.runState) !== -1
  }

  ColumnLayout {
    anchors.fill: parent
    spacing: 10

    RowLayout {
      id: controlRow
      Layout.fillWidth: true
      spacing: 12

      Label {
        text: qsTr("控制")
        font.bold: true
        color: Cores.CoreStyle.text
        Layout.fillWidth: true
      }

      Label {
        text: qsTr("状态: %1").arg(resolvedRunState())
        color: root.runState === "RUNNING" ? Cores.CoreStyle.success : Cores.CoreStyle.muted
      }

      Btns.ActionButton {
        text: qsTr("启动")
        enabled: Datas.StatusDatas.controlEnabled && root.hasProgram && root.runState !== "RUNNING"
        onClicked: startProgram()
      }

      Btns.ActionButton {
        text: qsTr("停止")
        danger: true
        enabled: Datas.StatusDatas.controlEnabled && isRunningOrPaused()
        onClicked: stopProgram()
      }

      Btns.ActionButton {
        text: qsTr("复位")
        danger: true
        enabled: Datas.StatusDatas.controlEnabled && isRunningOrPaused()
      }
      Btns.ActionButton {
        text: qsTr("重新执行")
        danger: true
        enabled: Datas.StatusDatas.controlEnabled && isRunningOrPaused()
      }
    }
  }
}
