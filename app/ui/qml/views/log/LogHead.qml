import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../cores" as Cores
import "../../Sockets" as Sockets
import "../../components/btns" as Btns
Item{
    height: Cores.CoreStyle.cardHeadHeight
    Layout.fillWidth: true
RowLayout {
  anchors.fill: parent
  spacing: 10
  Label { text: '鏃ュ織'; font.bold: true; color: Cores.CoreStyle.text }
  Rectangle { width: 10; height: 10; radius: 5; color: Sockets.LogsSocket.logsConnected ? Cores.CoreStyle.success : Cores.CoreStyle.danger }
  Label { text: Sockets.LogsSocket.logsConnected ? '宸茶繛鎺? : '鏈繛鎺?; color: Sockets.LogsSocket.logsConnected ? Cores.CoreStyle.success : Cores.CoreStyle.danger }
  Item { Layout.fillWidth: true }
  Btns.CheckBoxBase {
        implicitHeight: 25
    text: '鑷姩婊氬姩'; checked: root.autoScroll; onToggled: root.autoScroll = checked
  }
  Btns.ActionButton {

    text: '娓呯┖'; onClicked: Sockets.LogsSocket.clearLogs() }
  Btns.ActionButton {

    text: '鏈湴娴嬭瘯'; onClicked: Sockets.LogsSocket.addLocalLog('INFO', 'UI', '鏈湴娴嬭瘯鏃ュ織 ' + new Date().toLocaleTimeString())
  }
}

}

