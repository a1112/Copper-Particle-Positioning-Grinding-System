import QtQuick.Layouts 1.15
import QtWebSockets 1.1
import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {


  id: win


  width: 1366; height: 820


  visible: true


  title: "铜粒子定位磨削系统"





  // Simple REST helpers; can be replaced by dedicated Api module later


  // Error dialog and helpers


  property string errorText: ""


  function showError(msg) {


    errorText = msg


    errorDialog.open()


  }


  Dialog {


    id: errorDialog


    title: "请求失败"


    modal: true


    standardButtons: Dialog.Ok


    visible: false


    contentItem: Text { text: errorText; wrapMode: Text.WordWrap; color: "white" }


    background: Rectangle { color: "#5b0000"; radius: 6 }


  }





  // API client singleton for QML


  Loader { id: apiLoader; source: 'Api/ApiClient.qml'; onLoaded: { item.root = win; item.showError = showError; item.setBase('http://' + settings.apiHost + ':' + settings.apiPort); item.setTimeout(5000) } }
  Connections { target: settings; function onApiPortChanged() { if (apiLoader.item) apiLoader.item.setBase('http://' + settings.apiHost + ':' + settings.apiPort) } function onApiHostChanged() { if (apiLoader.item) apiLoader.item.setBase('http://' + settings.apiHost + ':' + settings.apiPort) } }





  Column {


    anchors.fill: parent; spacing: 8; padding: 8


    Row {


      spacing: 8


      Button { text: "开始"; onClicked: apiLoader.item.startRun(function(_) {}, function(s,m){ console.log('start err', s, m) }) }


      Button { text: "停止"; onClicked: apiLoader.item.stopRun(function(_) {}, function(s,m){ console.log('stop err', s, m) }) }
      Button { text: "设置"; onClicked: settingsDrawer.open() }


      Rectangle { width: 10; height: 10; radius: 5; color: (ws.status===WebSocket.Open ? '#1cc88a' : (ws.status===WebSocket.Connecting ? '#f6c23e' : '#e74a3b')) }  Label { text: '连接: ' + (ws.status===WebSocket.Open ? '已连接' : (ws.status===WebSocket.Connecting ? '连接中' : '未连接')) }  Label { text: 'API: ' + settings.apiHost + ':' + settings.apiPort }


    }


    RowLayout {
      id: mainRow
      width: parent.width
      spacing: 8

      // Left: Video area
      Item {
        id: videoArea
        Layout.preferredWidth: 800
        Layout.preferredHeight: 450
        Rectangle { anchors.fill: parent; color: "#222"; radius: 4 }
        Image {
          id: video
          anchors.fill: parent
          fillMode: Image.PreserveAspectFit
          cache: false
          asynchronous: false
          source: 'image://camera/live?ts=' + Date.now()
        }
        Timer { id: t; interval: 120; running: true; repeat: true; onTriggered: video.source = 'image://camera/live?ts=' + Date.now() }
        Canvas {
          id: overlay
          anchors.fill: parent
          onPaint: {
            var ctx = getContext('2d');
            ctx.clearRect(0,0,width,height);
            // crosshair
            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(width/2 - 20, height/2);
            ctx.lineTo(width/2 + 20, height/2);
            ctx.moveTo(width/2, height/2 - 20);
            ctx.lineTo(width/2, height/2 + 20);
            ctx.stroke();
            // target
            if (backend.targetX >= 0 && backend.targetY >= 0) {
              var x = backend.targetX * width / 640;
              var y = backend.targetY * height / 360;
              ctx.strokeStyle = '#FFCC00';
              ctx.beginPath();
              ctx.arc(x, y, 12, 0, Math.PI*2);
              ctx.stroke();
              ctx.fillStyle = '#FFCC00';
              ctx.fillText('θ=' + backend.targetTheta.toFixed(2) + ' s=' + backend.targetScore.toFixed(2), x+14, y-14);
            }
          }
        }
      }

      // Right: Instruction editor
      Rectangle {
        id: editorPanel
        Layout.fillWidth: true
        Layout.preferredHeight: videoArea.Layout.preferredHeight
        radius: 4
        color: "#1e1e1e"; border.color: "#333"
        ColumnLayout { anchors.fill: parent; anchors.margins: 8; spacing: 6
          RowLayout { Layout.fillWidth: true
            Label { text: "指令编辑"; font.bold: true; Layout.fillWidth: true }
            Button { text: "运行" }
            Button { text: "停止" }
            Button { text: "打开" }
            Button { text: "保存" }
          }
          TextArea {
            id: editor
            Layout.fillWidth: true
            Layout.fillHeight: true
            wrapMode: TextEdit.NoWrap
            font.family: "Consolas, 'Courier New', monospace"
            placeholderText: "在此编辑指令（支持 G/M 指令高亮；; 为注释）"
            Component.onCompleted: { if (pyHighlighter && editor.textDocument) pyHighlighter.attach(editor.textDocument) }
          }
        }
      }
    }    // WebSocket status updates and fallback polling


    WebSocket {


      id: ws


      url: 'ws://' + settings.apiHost + ':' + settings.apiPort + '/ws'


      active: true


      onStatusChanged: function(status) {


        if (status === WebSocket.Error) {


          showError("WS 连接错误: " + errorString)


          reconnectTimer.restart()


        } else if (status === WebSocket.Closed) {


          reconnectTimer.restart()


        }


      }


      onTextMessageReceived: function(message) {


        try {


          var st = JSON.parse(message)


          if (!st || !st.position) return


          backend._status = 'State: ' + st.state + ' | X ' + Number(st.position.x||0).toFixed(2) + ' Y ' + Number(st.position.y||0).toFixed(2)


          backend.statusChanged()


        } catch(e) { console.log('WS parse error:', e) }


      }


    }


    Timer {


      id: reconnectTimer


      interval: 3000; repeat: false


      onTriggered: { if (ws.status !== WebSocket.Open) { ws.active = false; ws.active = true } }


    }


    Timer {


      id: statusPoller


      interval: 1500; repeat: true


      running: ws.status !== WebSocket.Open


      onTriggered: apiLoader.item.status(function(st){


        if (!st || !st.position) return;


        backend._status = 'State: ' + st.state + ' | X ' + Number(st.position.x||0).toFixed(2) + ' Y ' + Number(st.position.y||0).toFixed(2)


        backend.statusChanged()


      }, function(s,m){ })


    }


    Row {


      spacing: 16


      Rectangle { width: 420; height: 180; color: '#1e1e1e'; radius: 4; border.color: '#333'


        Column { anchors.fill: parent; anchors.margins: 8; spacing: 6


          Label { text: '通信'; font.bold: true }


          Loader { source: 'views/CommPanel.qml' }


        }


      }


      Rectangle { width: 420; height: 180; color: '#1e1e1e'; radius: 4; border.color: '#333'


        Column { anchors.fill: parent; anchors.margins: 8; spacing: 6


          Label { text: '运动'; font.bold: true }


          Loader { id: motionLoader; source: 'views/MotionPanel.qml'; onLoaded: { if (item) item.api = apiLoader.item } }


        }


      }


      Rectangle { width: 420; height: 180; color: '#1e1e1e'; radius: 4; border.color: '#333'


        Column { anchors.fill: parent; anchors.margins: 8; spacing: 6


          Label { text: '安全'; font.bold: true }


          Loader { source: 'views/SafetyPanel.qml' }


        }


      }


    }


    // poll status to refresh label


    Timer {


      interval: 600; running: true; repeat: true


      onTriggered: apiLoader.item.status(function(st){


        if (!st || !st.position) return;


        backend._status = 'State: ' + st.state + ' | X ' + Number(st.position.x||0).toFixed(2) + ' Y ' + Number(st.position.y||0).toFixed(2)


        backend.statusChanged()


      }, function(s,m){ /* ignore transient errors */ })


    }


    TextArea { readOnly: true; text: backend.logs; height: 160; wrapMode: Text.WordWrap }


  }

  // Settings drawer (repurposed from old editor drawer)
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
          Label { text: "刷新间隔(ms)" }
          SpinBox { from: 50; to: 1000; value: 120; onValueModified: t.interval = value }
        }
        RowLayout {
          Button { text: "保存并重启 API"; onClicked: { settings.saveAndRestart(); } }
          Item { Layout.fillWidth: true }
          Button { text: "关闭"; onClicked: settingsDrawer.close() }
        }
      }
    }
  }
  }





























