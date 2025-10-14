import QtQuick
import QtQuick.Controls
import "../../cores" as Cores
import "." as Charts

// 复用 LineChart，设置默认样式与对外 API
GroupBox {
  id: root
  // 对外属性（转发给内部通用图表）
  property var series: []
  property int maxPoints: 240
  property real sampleIntervalSec: 0.5
  property color lineColor: Cores.CoreStyle.accent
  property color gridColor: "#223"
  property color axisColor: Cores.CoreStyle.muted
  property int yDecimals: 0
  function repaint(){ chart.repaint() }

  Charts.LineChart {
    id: chart
    anchors.fill: parent
    title: "主轴转速 (rpm)"
    series: root.series
    maxPoints: root.maxPoints
    sampleIntervalSec: root.sampleIntervalSec
    lineColor: root.lineColor
    gridColor: root.gridColor
    axisColor: root.axisColor
    yDecimals: root.yDecimals
    emptyText: "无转速数据"
  }
}

