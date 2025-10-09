import QtWebSockets 1.1
import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {


  id: win


  width: 1024; height: 640


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


  Loader { id: apiLoader; source: 'Api/ApiClient.qml'; onLoaded: { item.root = win; item.showError = showError; item.setBase('http://127.0.0.1:8000'); item.setTimeout(5000) } }





  Column {


    anchors.fill: parent; spacing: 8; padding: 8


    Row {


      spacing: 8


      Button { text: "开始"; onClicked: apiLoader.item.startRun(function(_) {}, function(s,m){ console.log('start err', s, m) }) }


      Button { text: "停止"; onClicked: apiLoader.item.stopRun(function(_) {}, function(s,m){ console.log('stop err', s, m) }) }


      Label { text: backend.status }


    }


    Rectangle { anchors.horizontalCenter: parent.horizontalCenter; width: 640; height: 360; color: "#222"; radius: 4


      Image {


        id: video


        anchors.fill: parent


        fillMode: Image.PreserveAspectFit


        cache: false


        source: 'http://127.0.0.1:8000/image.png?ts=' + Date.now()


      }


      // timer to refresh http image source via query param


      Timer { id: t; interval: 120; running: true; repeat: true; onTriggered: video.source = 'http://127.0.0.1:8000/image.png?ts=' + Date.now() }


      Canvas {


        id: overlay


        anchors.fill: parent


        onPaint: {


          var ctx = getContext('2d');


          ctx.clearRect(0,0,width,height);


          // draw crosshair at center


          ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 2;


          ctx.beginPath();


          ctx.moveTo(width/2 - 20, height/2);


          ctx.lineTo(width/2 + 20, height/2);


          ctx.moveTo(width/2, height/2 - 20);


          ctx.lineTo(width/2, height/2 + 20);


          ctx.stroke();





          // draw target result if available (coordinate assumes image pixels)


          if (backend.targetX >= 0 && backend.targetY >= 0) {


            var x = backend.targetX * width / 640; // naive scale, adjust if needed


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


    }    // WebSocket status updates and fallback polling


    WebSocket {


      id: ws


      url: "ws://127.0.0.1:8000/ws"


      active: true


      onStatusChanged: {


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


          backend.statusChanged.emit()


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


        backend.statusChanged.emit()


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


        backend.statusChanged.emit()


      }, function(s,m){ /* ignore transient errors */ })


    }


    TextArea { readOnly: true; text: backend.logs; height: 160; wrapMode: Text.WordWrap }


  }


}





















