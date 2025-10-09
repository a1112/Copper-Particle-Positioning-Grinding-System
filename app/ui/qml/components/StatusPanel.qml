import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtWebSockets 1.1

Rectangle {
  id: root
  property var backend
  property int wsStatus: WebSocket.Closed
  property real latency: -1
  property string apiHost: "127.0.0.1"
  property int apiPort: 8010

  radius: 4
  color: "#1e1e1e"; border.color: "#333"

  ColumnLayout { anchors.fill: parent; anchors.margins: 10; spacing: 8
    Label { text: "状态信息"; font.bold: true }
    RowLayout { Label { text: "工作状态"; Layout.preferredWidth: 72 }
      Label { text: backend ? backend.status : '' }
    }
    RowLayout {
      Label { text: "连接"; Layout.preferredWidth: 72 }
      Rectangle { width: 10; height: 10; radius: 5;
        color: (wsStatus===WebSocket.Open ? '#1cc88a' : (wsStatus===WebSocket.Connecting ? '#f6c23e' : '#e74a3b')) }
      Label { text: (wsStatus===WebSocket.Open ? '已连接' : (wsStatus===WebSocket.Connecting ? '连接中' : '未连接')) }
    }
    RowLayout { Label { text: "延迟"; Layout.preferredWidth: 72 }
      Label { text: (latency>=0 ? latency.toFixed(0) + ' ms' : '-') }
    }
    RowLayout { Label { text: "API"; Layout.preferredWidth: 72 }
      Label { text: apiHost + ':' + apiPort }
    }
    Rectangle { height: 1; color: '#333'; Layout.fillWidth: true }
    RowLayout { Label { text: "位置"; Layout.preferredWidth: 72 }
      Label { text: backend ? backend.posText : '' }
    }
    RowLayout { Label { text: "目标X"; Layout.preferredWidth: 72 }
      Label { text: backend ? backend.targetX.toFixed(2) : '' }
    }
    RowLayout { Label { text: "目标Y"; Layout.preferredWidth: 72 }
      Label { text: backend ? backend.targetY.toFixed(2) : '' }
    }
    RowLayout { Label { text: "角度θ"; Layout.preferredWidth: 72 }
      Label { text: backend ? backend.targetTheta.toFixed(2) : '' }
    }
    RowLayout { Label { text: "置信度"; Layout.preferredWidth: 72 }
      Label { text: backend ? backend.targetScore.toFixed(2) : '' }
    }
    Rectangle { height: 1; color: '#333'; Layout.fillWidth: true }
    RowLayout { Label { text: "门锁"; Layout.preferredWidth: 72 }
      Label { text: backend && backend.lockDoor ? 'OK' : 'NG'; color: backend && backend.lockDoor ? '#22c55e' : '#ef4444' }
    }
    RowLayout { Label { text: "真空"; Layout.preferredWidth: 72 }
      Label { text: backend && backend.lockVacuum ? 'OK' : 'NG'; color: backend && backend.lockVacuum ? '#22c55e' : '#ef4444' }
    }
    RowLayout { Label { text: "急停"; Layout.preferredWidth: 72 }
      Label { text: backend && backend.lockEStop ? 'NG' : 'OK'; color: backend && backend.lockEStop ? '#ef4444' : '#22c55e' }
    }
    RowLayout { Label { text: "回零"; Layout.preferredWidth: 72 }
      Label { text: backend && backend.lockHomed ? 'OK' : 'NG'; color: backend && backend.lockHomed ? '#22c55e' : '#ef4444' }
    }
    RowLayout { Label { text: "主轴"; Layout.preferredWidth: 72 }
      Label { text: backend && backend.lockSpindle ? 'OK' : 'NG'; color: backend && backend.lockSpindle ? '#22c55e' : '#ef4444' }
    }
    Item { Layout.fillHeight: true }
    RowLayout { Layout.alignment: Qt.AlignRight; Button { text: "刷新"; onClicked: backend && backend.refresh() } }
  }
}

