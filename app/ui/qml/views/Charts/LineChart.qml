import QtQuick
import QtQuick.Controls
import "../../cores" as Cores

// Generic line chart with grid, axes, time-based X labels
GroupBox {
  id: root
  property var series: []
  property int maxPoints: 240
  property real sampleIntervalSec: 0.5
  property color lineColor: Cores.CoreStyle.accent
  property color gridColor: "#223"
  property color axisColor: Cores.CoreStyle.muted
  property int yDecimals: 0
  property int xTicks: 4
  property int yTicks: 4
  property string emptyText: "No data"

  padding: 4
  function repaint(){ chart.requestPaint() }

  Canvas {
    id: chart
    anchors.fill: parent
    onPaint: {
      var ctx = getContext('2d')
      ctx.clearRect(0, 0, width, height)
      var data = root.series
      if (!data || !data.length) {
        ctx.fillStyle = Cores.CoreStyle.muted
        ctx.font = '12px sans-serif'
        ctx.fillText(root.emptyText, 8, 16)
        return
      }
      var n = Math.min(root.maxPoints, data.length)
      var arr = data.slice(data.length - n)
      var min = Math.min.apply(null, arr)
      var max = Math.max.apply(null, arr)
      if (min===max){ var pad = (min===0 ? 1 : Math.abs(min)*0.05); min -= pad; max += pad }
      // grid
      ctx.strokeStyle = root.gridColor
      ctx.lineWidth = 1
      ctx.beginPath()
      for (var i=0;i<=root.yTicks;i++){
        var y = i * (height/root.yTicks)
        ctx.moveTo(0, y); ctx.lineTo(width, y)
      }
      ctx.stroke()
      // axes + labels
      ctx.strokeStyle = root.gridColor
      ctx.beginPath(); ctx.moveTo(0, height-0.5); ctx.lineTo(width, height-0.5); ctx.stroke()
      ctx.fillStyle = root.axisColor
      ctx.font = '11px sans-serif'
      // Y labels
      for (var yi=0; yi<=root.yTicks; yi++){
        var yy = yi * (height/root.yTicks)
        var v = max - yi*(max-min)/root.yTicks
        var txt = (root.yDecimals>0 ? v.toFixed(root.yDecimals) : Math.round(v).toString())
        ctx.fillText(txt, 4, Math.min(height-2, Math.max(12, yy+2)))
      }
      // X time labels (right=0s)
      var totalSec = (n-1) * root.sampleIntervalSec
      for (var xi=0; xi<=root.xTicks; xi++){
        var xx = xi * (width/root.xTicks)
        var tsec = totalSec * (1 - xi/root.xTicks)
        var ttxt = (tsec<=0.05) ? '0s' : ('-' + tsec.toFixed(1) + 's')
        ctx.fillText(ttxt, Math.max(2, Math.min(width-28, xx-10)), height-4)
      }
      // line
      ctx.strokeStyle = root.lineColor; ctx.lineWidth = 1.5
      ctx.beginPath()
      for (var j=0;j<arr.length;j++){
        var x = j * (width/(n-1))
        var yv = height - (arr[j]-min)/(max-min) * height
        if (j===0) ctx.moveTo(x, yv); else ctx.lineTo(x, yv)
      }
      ctx.stroke()
    }
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
  }
}
