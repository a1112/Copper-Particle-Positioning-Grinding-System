import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../Sockets" as Sockets
import "../../cores" as Cores
import "../../Api" as Api

RowLayout {
  spacing: 8
  Rectangle { width: 10; height: 10; radius: 5; color: Sockets.StatusSocket.connected ? "#22c55e" : "#ef4444" }
  Label { text: Sockets.StatusSocket.connected ? "宸茶繛鎺? : "鏈繛鎺?; color: Cores.CoreStyle.text }
  Label {
    id: latency
    color: Cores.CoreStyle.muted
    text: {
      var ts = Sockets.StatusSocket.lastMsgTs || 0;
      if (ts<=0) return "寤惰繜: 0";
      var age = Math.max(0, Date.now() - ts);
      return "寤惰繜: " + age + " ms";
    }
  }
  Label { text: "API:"; color: Cores.CoreStyle.muted }
  Item {
    // Make the docs link show pointing-hand cursor on hover
    id: apiLink
    width: link.implicitWidth
    height: link.implicitHeight
    Text {
      id: link
      textFormat: Text.RichText
      color: Cores.CoreStyle.accent
      readonly property string base: Api.Urls.base()
      text: "<a href='" + base + "/docs'>" + Cores.CoreSettings.apiHost + ":" + Cores.CoreSettings.apiPort + "/docs</a>"
      onLinkActivated: function(url){ Qt.openUrlExternally(url) }
    }
    MouseArea {
      anchors.fill: parent
      hoverEnabled: true
      acceptedButtons: Qt.NoButton
      cursorShape: Qt.PointingHandCursor
    }
  }
}

