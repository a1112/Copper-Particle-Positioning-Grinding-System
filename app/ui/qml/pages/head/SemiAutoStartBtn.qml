import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

import "../../cores" as Cores
import "../../Api" as Api
import "../../datas" as Datas
import "../../works" as Works

Rectangle {
  id: startBtn
  property bool running: false
  property bool hovered: false
  property bool busy: false
  readonly property color accentColor: running ? Cores.CoreStyle.danger : Cores.CoreStyle.success
  readonly property color baseColor: hovered
                                  ? Qt.darker(accentColor, running ? 1.05 : 1.15)
                                  : Qt.darker(accentColor, running ? 1.25 : 1.35)
  readonly property color highlightColor: Qt.lighter(accentColor, running ? 1.25 : 1.45)
  readonly property color labelColor: running ? "#f8fafc" : "#0f172a"
  readonly property bool canStart: Datas.TaskDatas.executeReady
  readonly property bool controlEnabled: Datas.StatusDatas.controlEnabled

  Layout.alignment: Qt.AlignVCenter
  Layout.preferredWidth: visible ? width : 0
  Layout.preferredHeight: visible ? height : 0
  visible: Cores.CoreState.currentRunModelIndex === 1
  enabled: !busy && controlEnabled && (running || (!Datas.TaskDatas.alarmLocked && canStart))
  height: Math.max(36, parent ? parent.height * 0.8 : 36)
  width: height * 2.4
  radius: 8
  color: baseColor
  border.color: highlightColor
  border.width: 1.2
  opacity: visible ? (enabled ? 1.0 : 0.5) : 0.0
  layer.enabled: true
  layer.effect: DropShadow {
    horizontalOffset: 0
    verticalOffset: 2
    radius: 12
    samples: 16
    color: "#40111111"
    transparentBorder: true
  }

  gradient: Gradient {
    GradientStop { position: 0.0; color: Qt.lighter(baseColor, 1.2) }
    GradientStop { position: 1.0; color: Qt.darker(baseColor, 1.15) }
  }

  Behavior on color { ColorAnimation { duration: 140 } }

  RowLayout {
    anchors.fill: parent
    anchors.margins: 6
    spacing: 6
    Image {
      source: Cores.CoreStyle.getIconSource(running ? "close.png" : "play.png")
      fillMode: Image.PreserveAspectFit
      Layout.preferredWidth: startBtn.height * 0.6
      Layout.preferredHeight: startBtn.height * 0.6
      opacity: running ? 0.85 : 1.0
    }
    Label {
      text: running ? qsTr("运行中") : qsTr("未运行")
      color: labelColor
      font.bold: true
      font.pixelSize: startBtn.height * 0.38
      opacity: running ? 0.9 : 1.0
      horizontalAlignment: Text.AlignHCenter
      verticalAlignment: Text.AlignVCenter
    }
  }

  MouseArea {
    anchors.fill: parent
    hoverEnabled: true
    enabled: startBtn.enabled
    cursorShape: Qt.PointingHandCursor
    onEntered: startBtn.hovered = true
    onExited: startBtn.hovered = false
    onClicked: {
      if (startBtn.busy)
        return
      if (running) {
        startBtn._stopRun()
      } else {
        startBtn._startRunWithTask()
      }
    }
  }

  function _stopRun() {
    busy = true
    Api.ApiClient.stopRun(function() {
      busy = false
    }, function(_, msg) {
      busy = false
      var stopError = msg !== undefined ? msg : qsTr("stopRun 执行失败")
      Cores.CoreError.showError(stopError)
    })
  }

  function _startRunWithTask() {
    if (!Datas.TaskDatas.executeReady) {
      Cores.CoreError.showError(qsTr("执行准备未就绪"))
      return
    }
    busy = true
    Works.TaskWork.enqueueExecute(Datas.TaskDatas.readyRecordId, Datas.TaskDatas.workpieceId, function() {
      Api.ApiClient.startRun(function() {
        busy = false
      }, function(_, msg) {
        busy = false
        var startError = msg !== undefined ? msg : qsTr("startRun 调用失败！")
        Cores.CoreError.showError(startError)
      })
    }, function(_, msg) {
      busy = false
      var err = msg !== undefined ? msg : qsTr("enqueueExecute 调用失败！")
      Cores.CoreError.showError(err)
    })
  }
}


