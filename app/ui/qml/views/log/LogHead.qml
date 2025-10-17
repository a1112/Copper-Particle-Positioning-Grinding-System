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
    Label { text: "日志"; font.bold: true; color: Cores.CoreStyle.text }
    Rectangle { width: 10; height: 10; radius: 5; color: Datas.LogDatas.connected ? Cores.CoreStyle.success : Cores.CoreStyle.danger }
    Label { text: (Datas.LogDatas.connected ? "已连接" : "未连接"); color: (Datas.LogDatas.connected ? Cores.CoreStyle.success : Cores.CoreStyle.danger) }
    Item { Layout.fillWidth: true }
    Btns.ActionButton { text: "清空"; onClicked: Works.LogsWork.clearLocalLogs() }
    Btns.ActionButton { text: "服务器测试"; onClicked: Works.LogsWork.sendServerLog('测试 ' + new Date().toLocaleTimeString()) }
    Btns.ActionButton { text: "清空服务器"; onClicked: Works.LogsWork.clearServerLogs() }
  }
}
