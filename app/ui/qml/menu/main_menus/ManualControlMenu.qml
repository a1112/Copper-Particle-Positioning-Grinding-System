import QtQuick.Controls
import "../../datas" as Datas
import "../../Api" as Api
import "../../works" as Works

Menu {
  title: qsTr("手动控制")

  function sendManual(action) {
    if (!Datas.StatusDatas.forceEnableControls && !Datas.StatusDatas.controlEnabled)
      return

    var params = {}
    if (Datas.TaskDatas.readyRecordId && Datas.TaskDatas.readyRecordId > 0)
      params.record_id = Datas.TaskDatas.readyRecordId
    else if (Datas.TaskDatas.latestRecordId && Datas.TaskDatas.latestRecordId > 0)
      params.record_id = Datas.TaskDatas.latestRecordId
    if (Datas.TaskDatas.workpieceId && Datas.TaskDatas.workpieceId > 0)
      params.workpiece_id = Datas.TaskDatas.workpieceId
    params.manual = true

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
    text: qsTr("缺陷检测")
    onTriggered: sendManual("manual.defect_detection_secondary")
  }

  MenuItem {
    text: qsTr("c5.上传指令")
    onTriggered: sendManual("manual.c5_upload")
  }

  MenuItem {
    text: qsTr("运行指令")
    onTriggered: sendManual("manual.run_command")
  }

  MenuItem {
    text: qsTr("清除上传的指令")
    onTriggered: sendManual("manual.clear_upload")
  }

  MenuItem {
    text: qsTr("初始化")
    onTriggered: sendManual("manual.initialize")
  }

  MenuItem {
    text: qsTr("初始化")
    onTriggered: sendManual("manual.initialize_secondary")
  }
}
