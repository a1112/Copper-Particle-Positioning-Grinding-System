import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../cores" as Cores
import "../../datas" as Datas
import "../../works" as Works
import "../../components/btns" as Btns

Item {
  height: Cores.CoreStyle.cardHeadHeight
  Layout.fillWidth: true

  RowLayout {
    anchors.fill: parent
    spacing: 10

    Label {
      text: qsTr("日志")
      font.bold: true
      color: Cores.CoreStyle.text
    }

    Rectangle {
      width: 10
      height: 10
      radius: 5
      color: Datas.LogDatas.connected ? Cores.CoreStyle.success : Cores.CoreStyle.danger
    }

    Label {
      text: Datas.LogDatas.connected ? qsTr("已连接") : qsTr("未连接")
      color: Datas.LogDatas.connected ? Cores.CoreStyle.success : Cores.CoreStyle.danger
    }

    Item { Layout.fillWidth: true }

    Btns.ActionButton {
      text: qsTr("清空本地")
      onClicked: Works.LogsWork.clearLocalLogs()
    }

    Btns.ActionButton {
      text: qsTr("发送测试日志")
      onClicked: Works.LogsWork.sendServerLog(qsTr("测试日志 ") + new Date().toLocaleTimeString())
    }

    Btns.ActionButton {
      text: qsTr("清空服务器")
      onClicked: Works.LogsWork.clearServerLogs()
    }
  }
}

