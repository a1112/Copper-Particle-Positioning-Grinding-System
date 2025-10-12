import QtQuick
import QtQuick.Controls
import "../../cores" as Cores
import "." as Charts

// 复用 LineChart，设置默认样式与对外 API
GroupBox {
  id: root
  property var series: []
  property int maxPoints: 240
  property real sampleIntervalSec: 0.5
  property color lineColor: Cores.CoreStyle.info
  property color gridColor: "#223"
  property color axisColor: Cores.CoreStyle.muted
  property int yDecimals: 2
  function repaint(){ chart.repaint() }

  Charts.LineChart {
    id: chart
    anchors.fill: parent
    title: "主轴扭矩 (N·m)"
    series: root.series
    maxPoints: root.maxPoints
    sampleIntervalSec: root.sampleIntervalSec
    lineColor: root.lineColor
    gridColor: root.gridColor
    axisColor: root.axisColor
    yDecimals: root.yDecimals
    emptyText: "无扭矩数据"
  }
}
