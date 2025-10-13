import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../head" as Widgets
import "../../../cores" as Cores
import "../../../Sockets" as Sockets
import "../../../views" as Views
import "../../../Api" as Api

// 测试页面：用于快速验证主题、时间、小图表与API链接
Item {
  id: root
  Layout.fillWidth: true
  Layout.fillHeight: true

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 12
    spacing: 10

    Label { text: "测试页面 TestPage"; font.pixelSize: 20; color: Cores.CoreStyle.text }

    RowLayout {
      spacing: 16
      Label { text: "当前主题:"; color: Cores.CoreStyle.muted }
      Label { text: Cores.CoreStyle.theme; color: Cores.CoreStyle.accent }
      Button { text: "切换主题(蓝)"; onClicked: Cores.CoreStyle.applyTheme("techBlue") }
      Button { text: "切换主题(绿)"; onClicked: Cores.CoreStyle.applyTheme("emerald") }
      Button { text: "切换主题(紫)"; onClicked: Cores.CoreStyle.applyTheme("nightPurple") }
    }

    RowLayout {
      spacing: 24
      Widgets.DateTimeView { timePixelSize: 28 }
      RowLayout {
        spacing: 8
        Label { text: "API:"; color: Cores.CoreStyle.muted }
        Text {
          textFormat: Text.RichText
          color: Cores.CoreStyle.accent
          readonly property string base: Api.Urls.base()
          text: "<a href='" + base + "/docs'>" + Cores.CoreSettings.apiHost + ":" + Cores.CoreSettings.apiPort + "/docs</a>"
          onLinkActivated: function(url){ Qt.openUrlExternally(url) }
        }
      }
    }

    GroupBox {
      title: "WS 最近消息"
      Layout.fillWidth: true
      Layout.preferredHeight: 140
      TextArea { anchors.fill: parent; readOnly: true; wrapMode: TextArea.Wrap; text: JSON.stringify(Sockets.Sockets.lastMessage||{}, null, 2) }
    }

    GroupBox {
      title: "seriesA 简易曲线"
      Layout.fillWidth: true
      Layout.preferredHeight: 160
      Canvas {
        id: chart
        anchors.fill: parent
        onPaint: {
          var ctx = getContext('2d');
          ctx.clearRect(0,0,width,height);
          var data = Sockets.Sockets.seriesA || [];
          if (!data.length) return;
          var n = Math.min(200, data.length);
          var arr = data.slice(data.length - n);
          var min = Math.min.apply(null, arr);
          var max = Math.max.apply(null, arr);
          if (min===max){ min -= 1; max += 1 }
          ctx.strokeStyle = Cores.CoreStyle.accent; ctx.lineWidth = 1.5;
          ctx.beginPath();
          for (var i=0;i<arr.length;i++){
            var x = i * (width/(n-1));
            var y = height - (arr[i]-min)/(max-min) * height;
            if (i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
          }
          ctx.stroke();
        }
        Connections { target: Sockets.Sockets; function onMessageReceived(p){ chart.requestPaint() } }
      }
    }

        GroupBox {
      title: "组件预览"
      Layout.fillWidth: true
      Layout.fillHeight: true
      SplitView {
        anchors.fill: parent
        // 左侧状态
        Views.StatusPanel { SplitView.preferredWidth: 260; backend: backend }
        // 中间视频
        Views.VideoView { SplitView.preferredWidth: 720; backend: backend }
        // 右侧指令编辑
        Views.EditorPanel { SplitView.preferredWidth: 360 }
      }
    }    Item { Layout.fillHeight: true }
  }
}






