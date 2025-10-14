import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtWebSockets
import "../components/btns" as Btns
import "../Api" as Api

Rectangle {
  id: root
  property var backend
  property int wsStatus: WebSocket.Closed
  property real latency: -1
  property string apiHost: "127.0.0.1"
  property int apiPort: 8010
  property var machineMeta: ({})

  radius: 4
  color: "#1e1e1e"; border.color: "#333"

  Component.onCompleted: {
    try { Api.ApiClient.get('/config/meta', function(r){ root.machineMeta = r||{} }, function(s,m){ console.log('meta err', s, m) }) } catch(e){}
  }

  ColumnLayout {
    anchors.fill: parent;
    anchors.margins: 10;
    spacing: 8
    Label { text: "状态信息"; font.bold: true }

    RowLayout { Label { text: "工作状态"; Layout.preferredWidth: 72 }
      Label { text: backend ? backend.status : '' }
    }

    RowLayout { Label { text: "连接"; Layout.preferredWidth: 72 }
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

    RowLayout { Label { text: "X"; Layout.preferredWidth: 72 }
      Label { text: backend ? backend.targetX.toFixed(2) : '' }
    }

    RowLayout { Label { text: "Y"; Layout.preferredWidth: 72 }
      Label { text: backend ? backend.targetY.toFixed(2) : '' }
    }

    RowLayout { Label { text: "Theta"; Layout.preferredWidth: 72 }
      Label { text: backend ? backend.targetTheta.toFixed(2) : '' }
    }

    RowLayout { Label { text: "置信度"; Layout.preferredWidth: 72 }
      Label { text: backend ? backend.targetScore.toFixed(2) : '' }
    }

    Rectangle { height: 1; color: '#333'; Layout.fillWidth: true }

    // 静态信息（来自配置/知识库）
    Label { text: "设备信息"; font.bold: true }

    RowLayout { Label { text: "刀盘直径"; Layout.preferredWidth: 72 }
      Label { text: (machineMeta.cutter_diameter || '-') }
    }

    RowLayout { Label { text: "刀具寿命"; Layout.preferredWidth: 72 }
      Label { text: (machineMeta.tool_life || '-') }
    }

    RowLayout { Label { text: "控制方式"; Layout.preferredWidth: 72 }
      Label { text: (machineMeta.control_mode || '-') }
    }

    RowLayout { Label { text: "台模式"; Layout.preferredWidth: 72 }
      Label { text: (machineMeta.stage_mode || '-') }
    }

    Rectangle { height: 1; color: '#333'; Layout.fillWidth: true }

    // 生产指标（算法/统计项）
    Label { text: "生产指标"; font.bold: true }

    RowLayout { Label { text: "平面高度"; Layout.preferredWidth: 72 }
      Label { text: (machineMeta.plane_height || '-') }
    }

    RowLayout { Label { text: "流水号"; Layout.preferredWidth: 72 }
      Label { text: (machineMeta.board_serial || '-') }
    }

    RowLayout { Label { text: "粒子数量"; Layout.preferredWidth: 72 }
      Label { text: (machineMeta.particle_count || '-') }
    }

    Item { Layout.fillHeight: true }
    RowLayout { Layout.alignment: Qt.AlignRight;
      Btns.ActionButton { text: "刷新";
        onClicked: backend && backend.refresh()
      }
      }
  }
}
