import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../../Api" as Api
import "../../../cores" as Cores


Item {
  id: view
  Layout.fillWidth: true
  Layout.fillHeight: true
  Rectangle {
    anchors.fill: parent
    color: Cores.CoreStyle.background
    radius: 4
  }
  Image {
    id: img
    anchors.fill: parent
    fillMode: Image.PreserveAspectFit
    cache: false
    asynchronous: false
    source: Api.Urls.api('image.png') + '?ts=' + Date.now()
  }

  Canvas {
    id: overlay
    anchors.fill: parent
    onPaint: {
      var ctx = getContext('2d');
      ctx.clearRect(0,0,width,height);
      ctx.strokeStyle = '#22d3ee'; ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.moveTo(width/2 - 16, height/2); ctx.lineTo(width/2 + 16, height/2);
      ctx.moveTo(width/2, height/2 - 16); ctx.lineTo(width/2, height/2 + 16);
      ctx.stroke();
      var pts = root.pathPoints || [];
      if (pts.length >= 2){
        ctx.strokeStyle = '#10b981'; ctx.lineWidth = 2;
        ctx.beginPath();
        for (var i=0;i<pts.length;i++){
          var px = pts[i].x * width / 640.0;
          var py = pts[i].y * height / 360.0;
          if (i===0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
        }
        ctx.stroke();
        var sx = pts[0].x * width / 640.0, sy = pts[0].y * height / 360.0;
        var ex = pts[pts.length-1].x * width / 640.0, ey = pts[pts.length-1].y * height / 360.0;
        ctx.fillStyle = '#f59e0b'; ctx.beginPath(); ctx.arc(sx, sy, 4, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = '#ef4444'; ctx.beginPath(); ctx.arc(ex, ey, 4, 0, Math.PI*2); ctx.fill();
      }
    }
  }
}
