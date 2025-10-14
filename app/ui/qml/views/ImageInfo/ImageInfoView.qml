import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../Sockets" as Sockets
import "../../Api" as Api
// ��ʾͼ�� + �����ƶ�·������
import "../Base"
import "../../cores" as Cores
import "../../components/btns" as Btns

BaseCard {
  id: root
  property int refreshMs: 150
  // ��¼������·���㣨���� /ws �е� position.x/y��
  property bool recordPath: true
  property var pathPoints: []   // ����Ԫ��: {x: Number, y: Number}
  readonly property int maxPath: 2000

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 8
    spacing: 6

    RowLayout {
      Layout.fillWidth: true
      spacing: 8
      Label { text: "ͼ��/·��Ԥ��"; color: Cores.CoreStyle.text; font.pixelSize: 14 }
      Item { Layout.fillWidth: true }
      CheckBox { text: "��¼·��"; checked: root.recordPath; onToggled: root.recordPath = checked }
      Btns.ActionButton { text: "清除"; onClicked: { root.pathPoints = []; overlay.requestPaint() } }
      Btns.ActionButton { text: "刷新"; onClicked: { img.source = Api.Urls.api('image.png') + '?ts=' + Date.now() } }
    }

    Item {
      id: view
      Layout.fillWidth: true
      Layout.fillHeight: true
      Rectangle { anchors.fill: parent; color: Cores.CoreStyle.background; radius: 4 }
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
          // ��ʮ������
          ctx.strokeStyle = '#22d3ee'; ctx.lineWidth = 1.2;
          ctx.beginPath();
          ctx.moveTo(width/2 - 16, height/2); ctx.lineTo(width/2 + 16, height/2);
          ctx.moveTo(width/2, height/2 - 16); ctx.lineTo(width/2, height/2 + 16);
          ctx.stroke();

          // ��·�������� position ���� 640x360 �������꣩
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
            // ���/�յ���
            var sx = pts[0].x * width / 640.0, sy = pts[0].y * height / 360.0;
            var ex = pts[pts.length-1].x * width / 640.0, ey = pts[pts.length-1].y * height / 360.0;
            ctx.fillStyle = '#f59e0b'; ctx.beginPath(); ctx.arc(sx, sy, 4, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle = '#ef4444'; ctx.beginPath(); ctx.arc(ex, ey, 4, 0, Math.PI*2); ctx.fill();
          }
        }
      }
    }
  }

  // �� WS ������ץȡ position��״̬Ϊ MOVE ʱ��¼·��
  Connections {
    target: Sockets.Sockets
    function onMessageReceived(p) {
      try {
        if (!p || !root.recordPath) return;
        var pos = p.position || {};
        var st = p.state || '';
        if (st === 'MOVE' && pos.x !== undefined && pos.y !== undefined){
          var x = Number(pos.x), y = Number(pos.y);
          if (!isNaN(x) && !isNaN(y)){
            root.pathPoints.push({x:x, y:y});
            if (root.pathPoints.length > root.maxPath) root.pathPoints.shift();
            overlay.requestPaint();
          }
        }
      } catch(e) { /* ignore */ }
    }
  }
}

