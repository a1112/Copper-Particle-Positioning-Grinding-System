import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../Sockets" as Sockets
import "../Base"
import "../../cores" as Cores

BaseCard {
  id: root
  property bool autoScroll: true
  property int maxRows: 1000

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 8
    spacing: 6

    RowLayout {
      Layout.fillWidth: true
      spacing: 10
      Label { text: '日志'; font.bold: true; color: Cores.CoreStyle.text }
      Rectangle { width: 10; height: 10; radius: 5; color: Sockets.Sockets.logsConnected ? Cores.CoreStyle.success : Cores.CoreStyle.danger }
      Label { text: Sockets.Sockets.logsConnected ? '已连接' : '未连接'; color: Sockets.Sockets.logsConnected ? Cores.CoreStyle.success : Cores.CoreStyle.danger }
      Item { Layout.fillWidth: true }
      CheckBox { text: '自动滚动'; checked: root.autoScroll; onToggled: root.autoScroll = checked }
      Button { text: '清空'; onClicked: Sockets.Sockets.clearLogs() }
      Button { text: '本地测试'; onClicked: Sockets.Sockets.addLocalLog('INFO', 'UI', '本地测试日志 ' + new Date().toLocaleTimeString()) }
    }

    Frame {
      Layout.fillWidth: true
      Layout.fillHeight: true
      padding: 6
      ListView {
        id: list
        anchors.fill: parent
        model: Sockets.Sockets.logs
        delegate: RowLayout {
          width: list.width
          spacing: 8
          property color lvColor: (level==='ERROR'? '#ef4444' : (level==='WARN' || level==='WARNING' ? '#f59e0b' : Cores.CoreStyle.muted))
          Label { text: new Date(ts*1000).toLocaleTimeString(); color: Cores.CoreStyle.muted; Layout.preferredWidth: 92 }
          Label { text: level; color: lvColor; Layout.preferredWidth: 64 }
          Label { text: name; color: Cores.CoreStyle.muted; Layout.preferredWidth: 120; elide: Label.ElideRight }
          Label { text: msg; color: Cores.CoreStyle.text; Layout.fillWidth: true; wrapMode: Text.WordWrap }
        }
        ScrollBar.vertical: ScrollBar {}
      }
    }
  }

  Connections {
    target: Sockets.Sockets
    function onLogReceived(item){ if (root.autoScroll) list.positionViewAtEnd() }
  }
}
