import QtQuick
import QtQuick.Controls
import QtQuick.Layouts



Item {
  id: root
  anchors.fill: parent

  // Inputs from main.qml
  property var backend
  property var apiClient
  property var uiSettings
  // Pass in from parent; do not assume WebSocket here
  property int wsStatus: 0
  property real lastMsgTs: -1
  property real nowTs: 0
  property int refreshMs: 120

  ColumnLayout {
    anchors.fill: parent
    spacing: 8
    anchors.margins: 8

    // Top bar
    TopBar {
      onStartClicked: apiClient && apiClient.startRun(function(_) {}, function(s,m){ console.log('start err', s, m) })
      onStopClicked: apiClient && apiClient.stopRun(function(_) {}, function(s,m){ console.log('stop err', s, m) })
      onOpenSettings: settingsDrawer.open()
      onOpenTestImages: testDialog.openAndRefresh()
    }

    // Responsive hint
    Label {
      Layout.fillWidth: true
      horizontalAlignment: Text.AlignRight
      opacity: 0.6
      font.pixelSize: 11
      text: 'Size: ' + root.width + 'x' + root.height
    }

    // Main split view
    SplitView {
      id: mainSplit
      Layout.fillWidth: true
      Layout.fillHeight: true
      Layout.preferredHeight: 460

      // Left status
      StatusPanel {
        SplitView.minimumWidth: 220
        SplitView.preferredWidth: 260
        backend: root.backend
        wsStatus: root.wsStatus
        latency: (root.lastMsgTs>0 ? Math.max(0, root.nowTs - root.lastMsgTs) : -1)
        apiHost: uiSettings ? uiSettings.apiHost : '127.0.0.1'
        apiPort: uiSettings ? uiSettings.apiPort : 8010
      }

      // Middle video
    VideoView {
        implicitWidth: 800
        implicitHeight: 450
        SplitView.minimumWidth: 400
        SplitView.preferredWidth: 800
        refreshMs: root.refreshMs
        backend: root.backend
      }

      // Right editor
      EditorPanel {
        SplitView.minimumWidth: 280
        SplitView.preferredWidth: 420
      }
    }

    // Bottom-right connection status
    Item {
      Layout.fillWidth: true
      anchors.right: parent.right
      Row {
        spacing: 8
        Rectangle { width: 10; height: 10; radius: 5; color: (root.wsStatus===WebSocket.Open ? '#1cc88a' : (root.wsStatus===WebSocket.Connecting ? '#f6c23e' : '#e74a3b')) }
        Label { text: '连接: ' + (root.wsStatus===WebSocket.Open ? '已连接' : (root.wsStatus===WebSocket.Connecting ? '连接中' : '未连接')) }
        Label { text: '延迟: ' + (root.lastMsgTs>0 ? Math.max(0, root.nowTs - root.lastMsgTs) + ' ms' : '-') }
        Label { text: 'API: ' + (uiSettings ? (uiSettings.apiHost + ':' + uiSettings.apiPort) : '-') }
      }
    }
  }

  // Settings drawer
  Drawer {
    id: settingsDrawer
    edge: Qt.RightEdge
    width: 360
    height: parent.height
    modal: false
    interactive: true
    focus: true

    Rectangle { anchors.fill: parent; color: "#1e1e1e"; border.color: "#333"
      ColumnLayout { anchors.fill: parent; anchors.margins: 8; spacing: 8
        Label { text: "设置"; font.bold: true }
        RowLayout {
          Label { text: "示例开关"; Layout.fillWidth: true }
          Switch { checked: true }
        }
        RowLayout {
          Label { text: "API 地址"; Layout.preferredWidth: 80 }
          TextField { text: uiSettings ? uiSettings.apiHost : ''; onTextChanged: if(uiSettings) uiSettings.apiHost = text; placeholderText: "127.0.0.1" }
        }
        RowLayout {
          Label { text: "API 端口"; Layout.preferredWidth: 80 }
          SpinBox { from: 1; to: 65535; value: uiSettings ? uiSettings.apiPort : 8010; onValueModified: if(uiSettings) uiSettings.apiPort = value }
        }
        RowLayout {
          Label { text: "刷新间隔(ms)"; Layout.preferredWidth: 80 }
          SpinBox { from: 50; to: 1000; value: root.refreshMs; onValueModified: root.refreshMs = value }
        }
        RowLayout {
          Button { text: "保存并重启 API"; onClicked: { if(uiSettings){ settings.apiHost = uiSettings.apiHost; settings.apiPort = uiSettings.apiPort; settings.saveAndRestart(); } } }
          Item { Layout.fillWidth: true }
          Button { text: "关闭"; onClicked: settingsDrawer.close() }
        }
      }
    }
  }
}

