import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../cores" as Cores
import "../../components/Base" as BaseComponents

// Elevation area chart with optional 2D/3D toggle
GroupBox {
  id: root
  title: qsTr("Height Profile")

  property var points: []          // [{ s: Number, z: Number }]
  property var cuts: []            // [{ s: Number, z: Number, amount: Number }]
  property real base: 0.0          // baseline depth (reference plane)
  property color lineColor: Cores.CoreStyle.info
  property color fillColor: "#2b77cf66"
  property color gridColor: "#223"
  property color axisColor: Cores.CoreStyle.muted
  property color cutColor: Cores.CoreStyle.danger
  property int xTicks: 4
  property int yTicks: 4
  property string emptyText: qsTr("No path data")
  property int viewMode: 0   // 0 = 2D, 1 = 3D

  padding: 4

  function repaint() {
    if (chart && viewMode === 0)
      chart.requestPaint()
  }

  ColumnLayout {
    anchors.fill: parent
    spacing: 6

    RowLayout {
      Layout.fillWidth: true
      spacing: 8
      RowLayout {
        spacing: 6
        Repeater {
          model: [
            { label: qsTr("2D"), value: 0 },
            { label: qsTr("3D"), value: 1 }
          ]
          delegate: BaseComponents.ItemDelegateBase {
            required property var modelData
            readonly property bool selected: root.viewMode === modelData.value
            text: modelData.label
            onClicked: root.viewMode = modelData.value

            background: Rectangle {
              anchors.fill: parent
              radius: 10
              color: selected ? Cores.CoreStyle.accent : (parent.hovered ? Qt.lighter(Cores.CoreStyle.surface, 1.1) : "transparent")
              border.width: 1
              border.color: selected ? Cores.CoreStyle.accent : (parent.hovered ? Qt.lighter(Cores.CoreStyle.accent, 1.2) : Cores.CoreStyle.border)
              opacity: selected ? 0.3 : 1.0
            }

            contentItem: Label {
              text: parent.text
              font.bold: selected
              color: selected ? Cores.CoreStyle.text : (parent.hovered ? Cores.CoreStyle.accent : Cores.CoreStyle.muted)
              horizontalAlignment: Text.AlignHCenter
              verticalAlignment: Text.AlignVCenter
              padding: 4
            }
          }
        }
      }
    }

    Frame {
      Layout.fillWidth: true
      Layout.fillHeight: true
      padding: 8
      clip: true

      Canvas {
        id: chart
        anchors.fill: parent
        visible: root.viewMode === 0
        onPaint: {
          var ctx = getContext('2d')
          ctx.clearRect(0, 0, width, height)
          var pts = (root.points && root.points.length) ? root.points : []
          if (pts.length < 2){
            ctx.fillStyle = Cores.CoreStyle.muted
            ctx.font = '12px sans-serif'
            ctx.fillText(root.emptyText, 8, 16)
            return
          }
          var sMin = pts[0].s, sMax = pts[pts.length-1].s
          for (var i=0;i<pts.length;i++){ if (pts[i].s < sMin) sMin = pts[i].s; if (pts[i].s > sMax) sMax = pts[i].s }
          var zMin = pts[0].z, zMax = pts[0].z
          for (var j=0;j<pts.length;j++){ if (pts[j].z < zMin) zMin = pts[j].z; if (pts[j].z > zMax) zMax = pts[j].z }
          zMin = Math.min(zMin, root.base)
          zMax = Math.max(zMax, root.base)
          if (zMin===zMax){ var pad = (zMin===0 ? 1 : Math.abs(zMin)*0.05); zMin -= pad; zMax += pad }
          var sRange = Math.max(1e-6, sMax - sMin)
          var zRange = Math.max(1e-6, zMax - zMin)

          function mapX(s){ return (s - sMin) / sRange * (width-1) }
          function mapY(z){ return height - (z - zMin) / zRange * (height-1) }

          ctx.strokeStyle = root.gridColor; ctx.lineWidth = 1
          ctx.beginPath()
          for (var yi=0; yi<=root.yTicks; yi++){ var y = yi * (height/root.yTicks); ctx.moveTo(0,y); ctx.lineTo(width,y) }
          ctx.stroke()

          ctx.fillStyle = root.axisColor; ctx.font = '11px sans-serif'
          for (var xi=0; xi<=root.xTicks; xi++){
            var sTick = sMin + xi/root.xTicks * sRange
            var x = xi * (width/root.xTicks)
            var ttxt = sTick.toFixed(1)
            ctx.fillText(ttxt, Math.max(2, Math.min(width-28, x-8)), height-4)
          }
          for (var yi2=0; yi2<=root.yTicks; yi2++){
            var zTick = zMin + (root.yTicks-yi2)/root.yTicks * zRange
            var y2 = yi2 * (height/root.yTicks)
            ctx.fillText(zTick.toFixed(2), 2, Math.min(height-2, Math.max(12, y2+2)))
          }

          ctx.beginPath()
          var x0 = mapX(pts[0].s), y0 = mapY(pts[0].z)
          ctx.moveTo(x0, y0)
          for (var k=1;k<pts.length;k++){
            ctx.lineTo(mapX(pts[k].s), mapY(pts[k].z))
          }
          ctx.lineTo(mapX(pts[pts.length-1].s), mapY(root.base))
          ctx.lineTo(mapX(pts[0].s), mapY(root.base))
          ctx.closePath()
          ctx.fillStyle = root.fillColor
          ctx.fill()

          ctx.strokeStyle = root.lineColor; ctx.lineWidth = 1.5
          ctx.beginPath(); ctx.moveTo(x0, y0)
          for (var k2=1;k2<pts.length;k2++) ctx.lineTo(mapX(pts[k2].s), mapY(pts[k2].z))
          ctx.stroke()

          if (root.cuts && root.cuts.length){
            ctx.strokeStyle = root.cutColor; ctx.fillStyle = root.cutColor; ctx.lineWidth = 1
            for (var c=0;c<root.cuts.length;c++){
              var cs = mapX(root.cuts[c].s)
              var cutZ = root.cuts[c].z
              if (cutZ === undefined)
                cutZ = root.base
              if (cutZ === null)
                cutZ = root.base
              var cz = mapY(cutZ)
              ctx.beginPath(); ctx.moveTo(cs, height); ctx.lineTo(cs, Math.max(0, cz-6)); ctx.stroke()
              ctx.beginPath(); ctx.moveTo(cs-3, cz-6); ctx.lineTo(cs+3, cz-6); ctx.lineTo(cs, cz-12); ctx.closePath(); ctx.fill()
            }
          }
        }
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
      }

      Rectangle {
        anchors.fill: parent
        radius: 4
        color: Cores.CoreStyle.surface
        border.color: Cores.CoreStyle.border
        visible: root.viewMode === 1

        Label {
          anchors.centerIn: parent
          color: Cores.CoreStyle.muted
          text: qsTr("3D view coming soon")
        }
      }
    }
  }
}
