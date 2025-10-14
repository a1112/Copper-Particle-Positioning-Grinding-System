import QtQuick
import QtQuick.Controls
import "../../cores" as Cores

// Elevation area chart: X=path length (s), Y=depth relative to base (z)
GroupBox {
  id: root
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
  property string xLabel: "路径长度"
  property string yLabel: "深度(相对基准)"
  property string emptyText: "无路径数据"

  padding: 4
  function repaint(){ chart.requestPaint() }

  Canvas {
    id: chart
    anchors.fill: parent
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
      // Compute ranges
      var sMin = pts[0].s, sMax = pts[pts.length-1].s
      for (var i=0;i<pts.length;i++){ if (pts[i].s < sMin) sMin = pts[i].s; if (pts[i].s > sMax) sMax = pts[i].s }
      var zMin = pts[0].z, zMax = pts[0].z
      for (var j=0;j<pts.length;j++){ if (pts[j].z < zMin) zMin = pts[j].z; if (pts[j].z > zMax) zMax = pts[j].z }
      // Include base in range
      zMin = Math.min(zMin, root.base)
      zMax = Math.max(zMax, root.base)
      if (zMin===zMax){ var pad = (zMin===0 ? 1 : Math.abs(zMin)*0.05); zMin -= pad; zMax += pad }
      var sRange = Math.max(1e-6, sMax - sMin)
      var zRange = Math.max(1e-6, zMax - zMin)

      function mapX(s){ return (s - sMin) / sRange * (width-1) }
      function mapY(z){ return height - (z - zMin) / zRange * (height-1) }

      // grid
      ctx.strokeStyle = root.gridColor; ctx.lineWidth = 1
      ctx.beginPath()
      for (var yi=0; yi<=root.yTicks; yi++){ var y = yi * (height/root.yTicks); ctx.moveTo(0,y); ctx.lineTo(width,y) }
      ctx.stroke()

      // axes labels (simple)
      ctx.fillStyle = root.axisColor; ctx.font = '11px sans-serif'
      // X ticks
      for (var xi=0; xi<=root.xTicks; xi++){
        var sTick = sMin + xi/root.xTicks * sRange
        var x = xi * (width/root.xTicks)
        var ttxt = sTick.toFixed(1)
        ctx.fillText(ttxt, Math.max(2, Math.min(width-28, x-8)), height-4)
      }
      // Y ticks
      for (var yi2=0; yi2<=root.yTicks; yi2++){
        var zTick = zMin + (root.yTicks-yi2)/root.yTicks * zRange
        var y2 = yi2 * (height/root.yTicks)
        ctx.fillText(zTick.toFixed(2), 2, Math.min(height-2, Math.max(12, y2+2)))
      }

      // area under curve to baseline
      ctx.beginPath()
      // start from first point on curve
      var x0 = mapX(pts[0].s), y0 = mapY(pts[0].z)
      ctx.moveTo(x0, y0)
      for (var k=1;k<pts.length;k++){
        ctx.lineTo(mapX(pts[k].s), mapY(pts[k].z))
      }
      // to baseline at last
      ctx.lineTo(mapX(pts[pts.length-1].s), mapY(root.base))
      // back to baseline at first
      ctx.lineTo(mapX(pts[0].s), mapY(root.base))
      ctx.closePath()
      ctx.fillStyle = root.fillColor
      ctx.fill()

      // draw curve
      ctx.strokeStyle = root.lineColor; ctx.lineWidth = 1.5
      ctx.beginPath(); ctx.moveTo(x0, y0)
      for (var k2=1;k2<pts.length;k2++) ctx.lineTo(mapX(pts[k2].s), mapY(pts[k2].z))
      ctx.stroke()

      // cuts markers
      if (root.cuts && root.cuts.length){
        ctx.strokeStyle = root.cutColor; ctx.fillStyle = root.cutColor; ctx.lineWidth = 1
        for (var c=0;c<root.cuts.length;c++){
          var cs = mapX(root.cuts[c].s)
          var cz = mapY(root.cuts[c].z || root.base)
          // vertical tick
          ctx.beginPath(); ctx.moveTo(cs, height); ctx.lineTo(cs, Math.max(0, cz-6)); ctx.stroke()
          // small triangle marker
          ctx.beginPath(); ctx.moveTo(cs-3, cz-6); ctx.lineTo(cs+3, cz-6); ctx.lineTo(cs, cz-12); ctx.closePath(); ctx.fill()
        }
      }
    }
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
  }
}
