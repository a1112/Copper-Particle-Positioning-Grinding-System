import QtQuick
import QtQuick.Controls

Item {
  id: root
  property int refreshMs: 120
  property var backend

  Rectangle { anchors.fill: parent; color: "#222"; radius: 4 }
  Image {
    id: video
    anchors.fill: parent
    fillMode: Image.PreserveAspectFit
    cache: false
    asynchronous: false
    source: 'image://camera/live?ts=' + Date.now()
  }
  Timer { interval: refreshMs; running: true; repeat: true; onTriggered: video.source = 'image://camera/live?ts=' + Date.now() }
  Canvas {
    id: overlay
    anchors.fill: parent
    onPaint: {
      var ctx = getContext('2d');
      ctx.clearRect(0,0,width,height);
      ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(width/2 - 20, height/2);
      ctx.lineTo(width/2 + 20, height/2);
      ctx.moveTo(width/2, height/2 - 20);
      ctx.lineTo(width/2, height/2 + 20);
      ctx.stroke();
      if (backend && backend.targetX >= 0 && backend.targetY >= 0) {
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

