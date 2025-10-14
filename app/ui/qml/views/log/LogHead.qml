import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../cores" as Cores
import "../../Sockets" as Sockets
import "../../components/btns" as Btns

Item {
  height: Cores.CoreStyle.cardHeadHeight
  Layout.fillWidth: true
  RowLayout {
    anchors.fill: parent
    spacing: 10
    Label { text: "日志"; font.bold: true; color: Cores.CoreStyle.text }
    Rectangle { width: 10; height: 10; radius: 5; color: Sockets.LogsSocket.logsConnected ? Cores.CoreStyle.success : Cores.CoreStyle.danger }
    Label { text: (Sockets.LogsSocket.logsConnected ? "已连接" : "未连接"); color: (Sockets.LogsSocket.logsConnected ? Cores.CoreStyle.success : Cores.CoreStyle.danger) }
    Item { Layout.fillWidth: true }
    Btns.ActionButton { text: "清空"; onClicked: Sockets.LogsSocket.clearLogs() }
    Btns.ActionButton { text: "服务器测试"; onClicked: Sockets.LogsSocket.sendServerLog('测试 ' + new Date().toLocaleTimeString()) }
    Btns.ActionButton { text: "清空服务器"; onClicked: Sockets.LogsSocket.clearServerLogs() }
  }
}
