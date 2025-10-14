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
    LogHead{
    }
    Frame {
      Layout.fillWidth: true
      Layout.fillHeight: true
      padding: 6
      ListView {
        id: list
        anchors.fill: parent
        model: Sockets.LogsSocket.logs
        delegate: RowLayout {
          width: list.width
          spacing: 8
          property color lvColor: (level==='ERROR'? '#ef4444' : (level==='WARN' || level==='WARNING' ? '#f59e0b' : Cores.CoreStyle.muted))
          Label { text: (time && time.length>0) ? time.split(' ')[1] : new Date(ts*1000).toLocaleTimeString(); color: Cores.CoreStyle.muted; Layout.preferredWidth: 92 }
          Label { text: level; color: lvColor; Layout.preferredWidth: 64 }
          Label { text: name; color: Cores.CoreStyle.muted; Layout.preferredWidth: 120; elide: Label.ElideRight }
          Label { text: msg; color: Cores.CoreStyle.text; Layout.fillWidth: true; wrapMode: Text.WordWrap }
        }
        ScrollBar.vertical: ScrollBar {}
      }
    }
  }

  Connections {
    target: Sockets.LogsSocket
    function onLogReceived(item){ if (root.autoScroll) list.positionViewAtEnd() }
  }
}



