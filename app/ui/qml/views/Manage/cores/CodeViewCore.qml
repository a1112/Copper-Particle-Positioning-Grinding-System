import QtQuick

// Core object providing selectable subviews (mirrors InfoViewCore API)
BaseCore {
  id: codeCore

  views: [
    {
      key: "cuttingStats",
      title: qsTr("切削统计"),
      source: Qt.resolvedUrl("../../DriveInfo/CuttingStatisticsView.qml")
    },
    {
      key: "singleCutStatus",
      title: qsTr("单次切削状态"),
      source: Qt.resolvedUrl("../../DriveInfo/SingleCutCommandStatusView.qml")
    },
    // {
    //   key: "codeEditor",
    //   title: qsTr("代码编辑"),
    //   source: Qt.resolvedUrl("../../Code/CodeView.qml")
    // },
    // {
    //   key: "codeControls",
    //   title: qsTr("运行控制"),
    //   source: Qt.resolvedUrl("../../Code/CodeContorl.qml")
    // },
  ]

  selectedKeys: ["codeEditor", "cuttingStats", "singleCutStatus"]
}
