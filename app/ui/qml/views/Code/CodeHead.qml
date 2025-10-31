import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../Api" as Api
import "../../cores" as Cores
import "../../components/btns" as Btns
import "../../datas" as Datas
import "../Base"

Item {
  id: headRoot
  signal backRequested()

  height: Cores.CoreStyle.cardHeadHeight
  Layout.fillWidth: true
  required property bool codeConnected
  required property string runState
  required property int currentIndex

  function resolvedState() {
    var stateValue = headRoot.runState
    if (stateValue === undefined || stateValue === null || stateValue === "")
      return qsTr("-")
    return stateValue
  }

  RowLayout {
    anchors.fill: parent
    spacing: 6

    ToolButton {
      text: "\u2190"
      onClicked: headRoot.backRequested()
      Layout.preferredWidth: 32
      Layout.preferredHeight: 24
    }

    Label {
      text: qsTr("指令")
      color: Cores.CoreStyle.text
      font.bold: true
      Layout.fillWidth: true
    }

    Rectangle {
      width: 10
      height: 10
      radius: 5
      color: headRoot.codeConnected ? Cores.CoreStyle.success : Cores.CoreStyle.danger
      Layout.alignment: Qt.AlignVCenter
    }



    Label {
      text: qsTr("当前: %1").arg(headRoot.currentIndex >= 0 ? headRoot.currentIndex + 1 : "-")
      color: Cores.CoreStyle.muted
    }
    Item{
      Layout.fillWidth: true
      height: 1
    }
    Btns.ActionButton {
      text: qsTr("运行")
      enabled: Datas.StatusDatas.controlEnabled && !Datas.TaskDatas.alarmLocked
      onClicked: Api.ApiClient.startRun()
    }

    Btns.ActionButton {
      text: qsTr("停止")
      danger: true
      enabled: Datas.StatusDatas.controlEnabled
      onClicked: Api.ApiClient.stopRun()
    }
  }
}

