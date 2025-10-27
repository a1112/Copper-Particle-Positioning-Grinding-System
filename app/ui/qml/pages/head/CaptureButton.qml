import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../cores" as Cores
import "../../datas" as Datas
import "../../Api" as Api
import "../../works" as Works

Rectangle {
  id: captureBtn
  property bool busy: false
  readonly property bool isFullAuto: Cores.CoreState.currentRunModelIndex === 0
  readonly property bool readyByStatus: captureBtn._statusReady()
  readonly property bool controlEnabled: Datas.StatusDatas.controlEnabled

  Layout.alignment: Qt.AlignVCenter
  visible: !isFullAuto
  enabled: !busy && !isFullAuto && readyByStatus && Datas.TaskDatas.captureReady && controlEnabled
  implicitHeight: Math.max(34, parent ? parent.height * 0.75 : 34)
  implicitWidth: implicitHeight * 2.1
  radius: 8
  color: enabled ? Cores.CoreStyle.info : Cores.CoreStyle.muted
  border.color: enabled ? Qt.lighter(color, 1.2) : Cores.CoreStyle.border
  opacity: visible ? 1.0 : 0.0

  Text {
    anchors.centerIn: parent
    text: qsTr("采集")
    color: enabled ? "#0f172a" : "#cbd5f5"
    font.bold: true
    font.pixelSize: captureBtn.implicitHeight * 0.32
  }

  MouseArea {
    anchors.fill: parent
    enabled: captureBtn.enabled
    hoverEnabled: true
    cursorShape: Qt.PointingHandCursor
    onClicked: captureBtn.triggerCapture()
  }

  function _statusReady() {
    var snapshot = Datas.StatusDatas.lastMessage || {}
    var candidates = []
    if (snapshot.state !== undefined)
      candidates.push(snapshot.state)
    if (snapshot.runState !== undefined)
      candidates.push(snapshot.runState)
    if (snapshot.run_state !== undefined)
      candidates.push(snapshot.run_state)
    for (var i = 0; i < candidates.length; ++i) {
      var text = String(candidates[i] || "").trim()
      if (text.length === 0)
        continue
      var upper = text.toUpperCase()
      if (upper.indexOf("READY") !== -1)
        return true
      if (upper === "IDLE")
        return true
      if (upper === "RUNNING")
        return false
      if (text.indexOf("准备就绪") !== -1)
        return true
      if (text.indexOf("重新识别") !== -1)
        return true
    }
    return true
  }

  function triggerCapture() {
    if (busy)
      return
    busy = true
    var payload = {}
    if (Datas.TaskDatas.workpieceId)
      payload.workpiece_id = Datas.TaskDatas.workpieceId
    Api.ApiClient.post("/data/records/capture", payload, function(_) {
      busy = false
      Works.TaskWork.refresh()
    }, function(_, message) {
      busy = false
      Cores.CoreError.showError(message || qsTr("采集触发失败"))
    })
  }
}
