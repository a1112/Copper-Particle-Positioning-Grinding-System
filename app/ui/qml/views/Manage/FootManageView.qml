import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "cores"
import "../../cores" as Cores
import "../Log" as LogViews
import "../Charts" as ChartViews
import "../Control" as ControlViews

// Footer management view: align log stream with elevation chart and PTZ manual control.
SplitView {

  id: root
  spacing: 5
  Layout.fillWidth: true
  property FootViewCode footViewCode: FootViewCode{}
  LogViews.LogView {
    id: logView
    SplitView.fillWidth: true
    SplitView.fillHeight: true
    SplitView.minimumWidth: 320
  }

  ChartViews.ElevationAreaChart {
    id: elevationChart
    SplitView.preferredWidth: 400
    SplitView.fillHeight: true
    SplitView.minimumWidth: 300

  }

  ControlViews.PTZControl {
    id: ptzControl
    SplitView.fillHeight: true
    SplitView.minimumWidth: 220
  }
}
