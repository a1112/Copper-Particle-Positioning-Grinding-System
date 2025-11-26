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
  readonly property bool isFullAuto:Cores.CoreState.currentRunModelIndex === 0
  readonly property bool readyByStatus: Cores.CoreButtonState.captureReadyByStatus
  readonly property bool canTriggerCapture: Cores.CoreButtonState.captureAvailable
  property var _pendingAutoRunContext: null
  property bool _awaitingAutoRun: false
  property bool _observedCaptureRunning: false

  Layout.alignment: Qt.AlignVCenter
  enabled: Datas.StatusDatas.forceEnableControls || (!busy && canTriggerCapture)
  implicitHeight: Math.max(34, parent ? parent.height * 0.75 : 34)
  implicitWidth: implicitHeight * 2.1
  radius: 8
  color: enabled ? Cores.CoreStyle.info : Cores.CoreStyle.muted
  border.color: enabled ? Qt.lighter(color, 1.2) : Cores.CoreStyle.border

  Text {
    anchors.centerIn: parent
    text: captureBtn.isFullAuto ? qsTr("开始") : qsTr("采集")
    color: enabled ? "#0f172a" : "#cbd5f5"
    font.bold: true
    font.pixelSize: captureBtn.implicitHeight * 0.32
  }

  MouseArea {
    anchors.fill: parent
    enabled: Datas.StatusDatas.forceEnableControls || captureBtn.enabled
    hoverEnabled: true
    cursorShape: Qt.PointingHandCursor
    onClicked: captureBtn.triggerCapture()
  }

  function triggerCapture() {
    console.log("triggerCapture")
    if (busy)
      return
    busy = true
    var payload = {}
    if (Datas.TaskDatas.workpieceId)
      payload.workpiece_id = Datas.TaskDatas.workpieceId
    Api.ApiClient.post("/capture", payload, function(resp) {
      var context = captureBtn._buildCaptureContext(resp, payload)
      captureBtn._updateCurrentEntities(resp, context.recordId, context.workpieceId)
      captureBtn._dispatchCaptureControl(context.controlParams)
      if (captureBtn.isFullAuto) {
        captureBtn._pendingAutoRunContext = context
        captureBtn._awaitingAutoRun = true
        captureBtn._observedCaptureRunning = false
      } else {
        busy = false
      }
    }, function(_, message) {
      busy = false
      captureBtn._pendingAutoRunContext = null
      captureBtn._awaitingAutoRun = false
      Cores.CoreError.showError(message || qsTr("采集触发失败"))
    })
  }

  function _buildCaptureContext(resp, payload) {
    var recordId = captureBtn._resolveRecordId(resp)
    var workpieceId = captureBtn._resolveWorkpieceId(payload, resp)
    return {
      recordId: recordId,
      workpieceId: workpieceId,
      controlParams: captureBtn._buildControlParams(recordId, workpieceId)
    }
  }

  function _resolveRecordId(resp) {
    var recordId = 0
    if (resp && resp.record_id !== undefined)
      recordId = Number(resp.record_id)
    else if (resp && resp.record && resp.record.id !== undefined)
      recordId = Number(resp.record.id)
    else if (Datas.TaskDatas.readyRecordId > 0)
      recordId = Datas.TaskDatas.readyRecordId
    else if (Datas.TaskDatas.latestRecordId > 0)
      recordId = Datas.TaskDatas.latestRecordId
    if (isNaN(recordId))
      recordId = 0
    return recordId
  }

  function _resolveWorkpieceId(payload, resp) {
    if (resp && resp.workpiece && resp.workpiece.id !== undefined) {
      var respId = Number(resp.workpiece.id)
      if (!isNaN(respId) && respId > 0)
        return respId
    }
    var fromPayload = payload && payload.workpiece_id ? Number(payload.workpiece_id) : 0
    if (!isNaN(fromPayload) && fromPayload > 0)
      return fromPayload
    var fromState = Number(Datas.TaskDatas.workpieceId)
    if (!isNaN(fromState) && fromState > 0)
      return fromState
    return 0
  }

  function _buildControlParams(recordId, workpieceId) {
    var params = {}
    if (recordId > 0)
      params.record_id = recordId
    if (workpieceId > 0)
      params.workpiece_id = workpieceId
    return params
  }

  function _updateCurrentEntities(resp, recordId, workpieceId) {
    if (resp && resp.record)
      Cores.CoreCurrent.updateRecord(resp.record)
    else if (recordId > 0)
      Cores.CoreCurrent.updateRecord({ id: recordId })

    if (resp && resp.workpiece)
      Cores.CoreCurrent.updateWorkpiece(resp.workpiece)
    else if (workpieceId > 0) {
      Cores.CoreCurrent.updateWorkpiece({
        id: workpieceId,
        code: Datas.TaskDatas.workpieceCode,
        type: Datas.TaskDatas.workpieceType
      })
    }
  }

  function _dispatchCaptureControl(controlParams) {
    Cores.CoreCurrent.pushControl("capture", controlParams, { source: "capture_button" })
    Api.ApiClient.control("capture", controlParams, function() {
      Works.TaskWork.refresh()
    }, function(_, errMessage) {
      console.warn("capture control dispatch failed", errMessage)
      Works.TaskWork.refresh()
    })
  }

  function _autoExecuteAndRun(recordId, workpieceId, onCompleted) {
    if (!captureBtn.isFullAuto)
      return
    captureBtn._awaitingAutoRun = false
    var finalize = function() {
      captureBtn._pendingAutoRunContext = null
      captureBtn._observedCaptureRunning = false
      if (onCompleted)
        onCompleted()
    }
    var params = {}
    if (recordId > 0)
      params.record_id = recordId
    if (workpieceId > 0)
      params.workpiece_id = workpieceId
    Api.ApiClient.startRun(params, function() {
      finalize()
    }, function(_, msg) {
      finalize()
      var startError = msg !== undefined ? msg : qsTr("startRun 调用失败！")
      Cores.CoreError.showError(startError)
    })
  }

  function _tryAutoStartFromStatus() {
    if (!captureBtn._awaitingAutoRun)
      return
    if (!captureBtn._pendingAutoRunContext)
      return
    if (!captureBtn._observedCaptureRunning)
      return
    if (Cores.CoreButtonState.captureRunState !== "COMPLETED")
      return
    captureBtn._autoExecuteAndRun(
      captureBtn._pendingAutoRunContext.recordId,
      captureBtn._pendingAutoRunContext.workpieceId,
      function() { captureBtn.busy = false }
    )
  }

  function _monitorCaptureTask() {
    if (!captureBtn._awaitingAutoRun || !captureBtn._pendingAutoRunContext)
      return
    var task = Datas.TaskDatas.captureTask || {}
    var taskRecordId = Number(task.record_id)
    var pendingRecord = Number(captureBtn._pendingAutoRunContext.recordId)
    if (!pendingRecord || taskRecordId !== pendingRecord)
      return
    var status = Number(task.status)
    if (status === 0 || status === 1) {
      captureBtn._observedCaptureRunning = true
      return
    }
    if (status === 2 && captureBtn._observedCaptureRunning)
      captureBtn._tryAutoStartFromStatus()
  }

  Connections {
    target: Cores.CoreButtonState
    function onCaptureRunStateChanged() {
      captureBtn._tryAutoStartFromStatus()
    }
  }

  Connections {
    target: Datas.TaskDatas
    function onCaptureTaskChanged() { captureBtn._monitorCaptureTask() }
  }
}
