import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../Sockets" as Sockets
import "../../cores" as Cores

Item {
  Layout.fillWidth: true
  height: 30

  Frame { anchors.fill: parent }

  RowLayout {
    anchors.fill: parent
    spacing: 12


    Item{
      Layout.fillWidth: true
      height: 1
    }


    RowLayout {
      spacing: 8
      Rectangle { width: 10; height: 10; radius: 5; color: Sockets.Sockets.connected ? "#22c55e" : "#ef4444" }
      Label { text: Sockets.Sockets.connected ? "已连接" : "未连接"; color: Cores.CoreStyle.text }
      Label {
        id: latency
        color: Cores.CoreStyle.muted
        text: {
          var ts = Sockets.Sockets.lastMsgTs || 0;
          if (ts<=0) return "延迟: 0";
          var age = Math.max(0, Date.now() - ts);
          return "延迟: " + age + " ms";
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
          readonly property string base: U.Urls.base()
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
    Item{
      width: 15
      height: 1
    }

  }
}


