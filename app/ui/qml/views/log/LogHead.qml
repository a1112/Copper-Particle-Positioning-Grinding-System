import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../cores" as Cores
import "../../Sockets" as Sockets

Item{
    height: Cores.CoreStyle.CardHeadHeight
    Layout.fillWidth: true
RowLayout {
    anchors.fill: parent
  spacing: 10
  Label { text: '日志'; font.bold: true; color: Cores.CoreStyle.text }
  Rectangle { width: 10; height: 10; radius: 5; color: Sockets.Sockets.logsConnected ? Cores.CoreStyle.success : Cores.CoreStyle.danger }
  Label { text: Sockets.Sockets.logsConnected ? '已连接' : '未连接'; color: Sockets.Sockets.logsConnected ? Cores.CoreStyle.success : Cores.CoreStyle.danger }
  Item { Layout.fillWidth: true }
  CheckBox { text: '自动滚动'; checked: root.autoScroll; onToggled: root.autoScroll = checked }
  Button { text: '清空'; onClicked: Sockets.Sockets.clearLogs() }
  Button { text: '本地测试'; onClicked: Sockets.Sockets.addLocalLog('INFO', 'UI', '本地测试日志 ' + new Date().toLocaleTimeString()) }
}

}
