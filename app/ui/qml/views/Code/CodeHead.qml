import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../Api" as Api
import "../../cores" as Cores
import "../../components/btns" as Btns
import "../../datas" as Datas
import "../Base"


Item {
  height:Cores.CoreStyle.cardHeadHeight
  Layout.fillWidth: true
  required property bool codeConnected
  required property string runState
  required property int currentIndex

  function resolvedState() {
    var stateValue = root.runState
    if (stateValue === undefined)
      return "-"
    if (stateValue === null)
      return "-"
    if (stateValue === "")
      return "-"
    return stateValue
  }

RowLayout {
  id: root
  anchors.fill: parent



  Label {
    text: qsTr("G-code")
    color: Cores.CoreStyle.text
    font.bold: true
    Layout.fillWidth: true
  }

  Rectangle {
    width: 10
    height: 10
    radius: 5
    color: root.codeConnected ? Cores.CoreStyle.success : Cores.CoreStyle.danger
    Layout.alignment: Qt.AlignVCenter
  }

  Label {
    text: root.codeConnected ? qsTr("Connected") : qsTr("Disconnected")
    color: root.codeConnected ? Cores.CoreStyle.success : Cores.CoreStyle.danger
  }



  Label {
    text: qsTr("State: %1").arg(resolvedState())
    color: root.runState === "RUNNING" ? Cores.CoreStyle.success : Cores.CoreStyle.muted
  }

  Label {
    text: qsTr("Current line: %1").arg(root.currentIndex >= 0 ? root.currentIndex + 1 : "-")
    color: Cores.CoreStyle.muted
  }

  Btns.ActionButton {
    text: qsTr("Run")
    enabled: Datas.StatusDatas.controlEnabled && !Datas.TaskDatas.alarmLocked
    onClicked: Api.ApiClient.startRun()
  }

  Btns.ActionButton {
    text: qsTr("Stop")
    danger: true
    enabled: Datas.StatusDatas.controlEnabled
    onClicked: Api.ApiClient.stopRun()
  }
}
}


