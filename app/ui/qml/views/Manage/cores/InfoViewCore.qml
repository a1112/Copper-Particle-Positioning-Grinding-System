import QtQuick

BaseCore {
  id: root

  views: [
    {
      key: "runState",
      title: qsTr("运行信息"),
      source: Qt.resolvedUrl("../../DriveInfo/RunStateInfoView.qml")
    },
    {
      key: "toolInfo",
      title: qsTr("刀具信息"),
      source: Qt.resolvedUrl("../../DriveInfo/ToolInfoView.qml")
    },
    {
      key: "driveMetrics",
      title: qsTr("设备状态"),
      source: Qt.resolvedUrl("../../DriveInfo/DriveInfoView.qml")
    },
    {
      key: "statusLights",
      title: qsTr("状态指示"),
      source: Qt.resolvedUrl("../../DriveInfo/StatusLightAlarmView.qml")
    },
    {
      key: "torqueChart",
      title: qsTr("扭矩趋势"),
      source: Qt.resolvedUrl("../../Charts/TorqueChart.qml")
    },
    {
      key: "elevationChart",
      title: qsTr("高度剖面"),
      source: Qt.resolvedUrl("../../Charts/ElevationAreaChart.qml")
    }
  ]

  selectedKeys: ["statusLights", "driveMetrics", "toolInfo", "runState"]
}
