import QtCore
import QtQuick.Layouts 1.15
import QtWebSockets 1.1
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material
ApplicationWindow {

  Material.theme: Material.Dark
  id: win


  width: 1366; height: 820


  visible: true


  title: "铜粒子定位磨削系统"





  // Simple REST helpers; can be replaced by dedicated Api module later


  // Error dialog and helpers


  property string errorText: ""
  // Connection latency tracking (ms timestamps)
  property double lastMsgTs: 0
  property double nowTs: 0


  function showError(msg) {


    errorText = msg


    errorDialog.open()


  }


  Dialog {


    id: errorDialog


    title: "请求失败"
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: 480


    modal: true


    standardButtons: Dialog.Ok


    visible: false


    contentItem: Text { text: errorText; wrapMode: Text.WordWrap; color: "white"; width: 420 }


    background: Rectangle { color: "#5b0000"; radius: 6 }


  }





  // API client singleton for QML


    // UI-level settings persisted via Qt.labs.settings
  Settings {
    id: uiSettings
    property string apiHost: "127.0.0.1"
    property int apiPort: 8010
    property int refreshMs: 120
  }

  Loader { id: apiLoader; source: 'Api/ApiClient.qml'; onLoaded: { item.root = win; item.showError = showError; item.setBase('http://' + uiSettings.apiHost + ':' + uiSettings.apiPort); item.setTimeout(5000) } }
  // Drive latency label updates
  Timer { interval: 500; running: true; repeat: true; onTriggered: nowTs = Date.now() }





  Column {


    anchors.fill: parent; spacing: 8; padding: 8


    Row {


      spacing: 8


      Button { text: "开始"; onClicked: apiLoader.item.startRun(function(_) {}, function(s,m){ console.log('start err', s, m) }) }


      Button { text: "停止"; onClicked: apiLoader.item.stopRun(function(_) {}, function(s,m){ console.log('stop err', s, m) }) }
      Button { text: "设置"; onClicked: settingsDrawer.open() }


    }


    SplitView {
      id: mainSplit
      width: parent.width
      height: 460
      orientation: Qt.Horizontal

      // Far-Left: Status panel
      Rectangle {
        id: statusPanel
        SplitView.minimumWidth: 220
        SplitView.preferredWidth: 260
        radius: 4
        color: "#1e1e1e"; border.color: "#333"
        ColumnLayout { anchors.fill: parent; anchors.margins: 10; spacing: 8
          Label { text: "状态信息"; font.bold: true }
          RowLayout { Label { text: "工作状态"; Layout.preferredWidth: 72 }; Label { text: backend.status } }
          RowLayout { Label { text: "连接"; Layout.preferredWidth: 72 }
            Rectangle { width: 10; height: 10; radius: 5; color: (ws.status===WebSocket.Open ? '#1cc88a' : (ws.status===WebSocket.Connecting ? '#f6c23e' : '#e74a3b')) }
            Label { text: (ws.status===WebSocket.Open ? '已连接' : (ws.status===WebSocket.Connecting ? '连接中' : '未连接')) }
          }
          RowLayout { Label { text: "延迟"; Layout.preferredWidth: 72 }; Label { text: (lastMsgTs>0 ? Math.max(0, nowTs - lastMsgTs) + ' ms' : '-') } }
          RowLayout { Label { text: "API"; Layout.preferredWidth: 72 }; Label { text: uiSettings.apiHost + ':' + uiSettings.apiPort } }
          Rectangle { height: 1; color: '#333'; Layout.fillWidth: true }
          RowLayout { Label { text: "位置"; Layout.preferredWidth: 72 }; Label { text: backend.posText } }
          RowLayout { Label { text: "目标X"; Layout.preferredWidth: 72 }; Label { text: backend.targetX.toFixed(2) } }
          RowLayout { Label { text: "目标Y"; Layout.preferredWidth: 72 }; Label { text: backend.targetY.toFixed(2) } }
          RowLayout { Label { text: "角度θ"; Layout.preferredWidth: 72 }; Label { text: backend.targetTheta.toFixed(2) } }
          RowLayout { Label { text: "置信度"; Layout.preferredWidth: 72 }; Label { text: backend.targetScore.toFixed(2) } }
          Rectangle { height: 1; color: '#333'; Layout.fillWidth: true }
          RowLayout { Label { text: "门锁"; Layout.preferredWidth: 72 }; Label { text: backend.lockDoor ? 'OK' : 'NG'; color: backend.lockDoor ? '#22c55e' : '#ef4444' } }
          RowLayout { Label { text: "真空"; Layout.preferredWidth: 72 }; Label { text: backend.lockVacuum ? 'OK' : 'NG'; color: backend.lockVacuum ? '#22c55e' : '#ef4444' } }
          RowLayout { Label { text: "急停"; Layout.preferredWidth: 72 }; Label { text: backend.lockEStop ? 'NG' : 'OK'; color: backend.lockEStop ? '#ef4444' : '#22c55e' } }
          RowLayout { Label { text: "回零"; Layout.preferredWidth: 72 }; Label { text: backend.lockHomed ? 'OK' : 'NG'; color: backend.lockHomed ? '#22c55e' : '#ef4444' } }
          RowLayout { Label { text: "主轴"; Layout.preferredWidth: 72 }; Label { text: backend.lockSpindle ? 'OK' : 'NG'; color: backend.lockSpindle ? '#22c55e' : '#ef4444' } }
          Item { Layout.fillHeight: true }
          RowLayout { Layout.alignment: Qt.AlignRight; Button { text: "刷新"; onClicked: backend.refresh() } }
        }
      }

      // Left: Video area
      Item {
        id: videoArea
        implicitWidth: 800
        implicitHeight: 450
        SplitView.minimumWidth: 400
        SplitView.preferredWidth: 800
        Rectangle { anchors.fill: parent; color: "#222"; radius: 4 }
        Image {
          id: video
          anchors.fill: parent
          fillMode: Image.PreserveAspectFit
          cache: false
          asynchronous: false
          source: 'image://camera/live?ts=' + Date.now()
        }
        Timer { id: t; interval: uiSettings.refreshMs; running: true; repeat: true; onTriggered: video.source = 'image://camera/live?ts=' + Date.now() }
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
        SplitView.minimumWidth: 280
        SplitView.preferredWidth: 420
        radius: 4
        color: "#1e1e1e"; border.color: "#333"
        ColumnLayout { anchors.fill: parent; anchors.margins: 8; spacing: 6
          RowLayout { Layout.fillWidth: true
            Label { text: "指令编辑"; font.bold: true; Layout.fillWidth: true }
            ComboBox {
              id: presetBox
              model: ["模板: 通用", "模板: G 代码示例", "模板: M 代码示例"]
              onCurrentIndexChanged: {
                if (currentIndex === 1 && editor.text.length === 0) {
                  editor.text = "G0 X0 Y0 Z0\nG1 X10 Y10 F100\n";
                } else if (currentIndex === 2 && editor.text.length === 0) {
                  editor.text = "M3 S1000\nG4 P1 ; dwell 1s\nM5\n";
                }
              }
            }
            Button { text: "运行" }
            Button { text: "停止" }
            Button { text: "打开" }
            Button { text: "保存" }
          }
          // Editor with line numbers
          RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0
            Rectangle {
              id: gutter
              color: "#202020"
              width: 48
              Layout.fillHeight: true
              Text {
                id: lineNums
                anchors.right: parent.right
                anchors.rightMargin: 6
                y: editor.contentItem ? (editor.contentItem.y + 4) : 4
                text: editor.text.length ? (function(){ var a = editor.text.split('\n'); var s = ''; for (var i=0;i<a.length;i++){ s += (i+1) + "\n"; } return s; })() : '1\n'
                color: "#888"
                font.family: "Consolas, 'Courier New', monospace"
                font.pixelSize: 14
                wrapMode: Text.NoWrap
                horizontalAlignment: Text.AlignRight
                verticalAlignment: Text.AlignTop
              }
            }
            TextArea {
              id: editor
              Layout.fillWidth: true
              Layout.fillHeight: true
              wrapMode: TextEdit.NoWrap
              font.family: "Consolas, 'Courier New', monospace"
              placeholderText: "在此编辑指令（支持 G/M 指令高亮；; 为注释）"
              onTextChanged: lineNums.text = (function(){ var a = editor.text.split('\n'); var s=''; for (var i=0;i<a.length;i++){ s += (i+1) + "\n"; } return s; })()
              Component.onCompleted: { if (pyHighlighter && editor.textDocument) pyHighlighter.attach(editor.textDocument) }
            }
          }
        }
      }
    }    // WebSocket status updates and fallback polling


    WebSocket {


      id: ws


      url: 'ws://' + uiSettings.apiHost + ':' + uiSettings.apiPort + '/ws'


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
          lastMsgTs = Date.now()


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

  // Bottom-right connection status and latency
  Item {
    anchors.right: parent.right; anchors.bottom: parent.bottom; anchors.margins: 8
    Row {
      spacing: 8
      Rectangle { width: 10; height: 10; radius: 5; color: (ws.status===WebSocket.Open ? '#1cc88a' : (ws.status===WebSocket.Connecting ? '#f6c23e' : '#e74a3b')) }
      Label { text: '连接: ' + (ws.status===WebSocket.Open ? '已连接' : (ws.status===WebSocket.Connecting ? '连接中' : '未连接')) }
      Label { text: '延迟: ' + (lastMsgTs>0 ? Math.max(0, nowTs - lastMsgTs) + ' ms' : '-') }
      Label { text: 'API: ' + uiSettings.apiHost + ':' + uiSettings.apiPort }
    }
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
          Label { text: "API 地址"; Layout.preferredWidth: 80 }
          TextField { text: uiSettings.apiHost; onTextChanged: uiSettings.apiHost = text; placeholderText: "127.0.0.1" }
        }
        RowLayout {
          Label { text: "API 端口"; Layout.preferredWidth: 80 }
          SpinBox { from: 1; to: 65535; value: uiSettings.apiPort; onValueModified: uiSettings.apiPort = value }
        }
        RowLayout {
          Label { text: "刷新间隔(ms)"; Layout.preferredWidth: 80 }
          SpinBox { from: 50; to: 1000; value: uiSettings.refreshMs; onValueModified: uiSettings.refreshMs = value }
        }
        RowLayout {
          Button { text: "保存并重启 API"; onClicked: { settings.apiHost = uiSettings.apiHost; settings.apiPort = uiSettings.apiPort; settings.saveAndRestart(); } }
          Item { Layout.fillWidth: true }
          Button { text: "关闭"; onClicked: settingsDrawer.close() }
        }
      }
    }
  }
  }




































