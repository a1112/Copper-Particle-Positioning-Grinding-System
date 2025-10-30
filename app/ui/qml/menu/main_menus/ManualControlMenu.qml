import QtQuick.Controls
import "../../datas" as Datas
import "../../Api" as Api
import "../../works" as Works
import "../../cores" as Cores

Menu {
  title: qsTr("手动控制")

  function sendManual(action) {
    if (!Datas.StatusDatas.forceEnableControls && !Datas.StatusDatas.controlEnabled)
      return

    var params = {}
    var currentRecordId = Cores.CoreCurrent.record && Cores.CoreCurrent.record.id ? Number(Cores.CoreCurrent.record.id) : 0
    if (currentRecordId > 0)
      params.record_id = currentRecordId
    else if (Datas.TaskDatas.readyRecordId && Datas.TaskDatas.readyRecordId > 0)
      params.record_id = Datas.TaskDatas.readyRecordId
    else if (Datas.TaskDatas.latestRecordId && Datas.TaskDatas.latestRecordId > 0)
      params.record_id = Datas.TaskDatas.latestRecordId
    var currentWorkpieceId = Cores.CoreCurrent.workpiece && Cores.CoreCurrent.workpiece.id ? Number(Cores.CoreCurrent.workpiece.id) : 0
    if (currentWorkpieceId > 0)
      params.workpiece_id = currentWorkpieceId
    else if (Datas.TaskDatas.workpieceId && Datas.TaskDatas.workpieceId > 0)
      params.workpiece_id = Datas.TaskDatas.workpieceId
    params.manual = true

    if (params.workpiece_id && params.workpiece_id > 0) {
      Cores.CoreCurrent.updateWorkpiece({
        id: params.workpiece_id,
        code: Datas.TaskDatas.workpieceCode,
        type: Datas.TaskDatas.workpieceType
      })
    }
    if (params.record_id)
      Cores.CoreCurrent.updateRecord({ id: params.record_id })
    Cores.CoreCurrent.pushControl(action, params, { source: "manual_menu" })

    Api.ApiClient.control(action, params, function() {
      Works.TaskWork.refresh()
    }, function(_, errMessage) {
      console.warn("Manual control dispatch failed", action, errMessage)
      Works.TaskWork.refresh()
    })
  }

  MenuItem {
    text: qsTr("单帧采集")
    onTriggered: sendManual("manual.single_frame_capture")
  }

  MenuItem {
    text: qsTr("预处理 (ROI+聚类)")
    onTriggered: sendManual("manual.preprocess_roi_cluster")
  }

  MenuItem {
    text: qsTr("缺陷检测")
    onTriggered: sendManual("manual.defect_detection")
  }
  MenuItem {
    text: qsTr("c5.上传指令")
    onTriggered: sendManual("manual.c5_upload")
  }
  MenuItem {
    text: qsTr("清除上传的指令")
    onTriggered: sendManual("manual.clear_upload")
  }

  MenuItem {
    text: qsTr("运行指令")
    onTriggered: sendManual("manual.run_command")
  }
  MenuItem {
    text: qsTr("初始化")
    onTriggered: sendManual("manual.initialize")
  }
}
