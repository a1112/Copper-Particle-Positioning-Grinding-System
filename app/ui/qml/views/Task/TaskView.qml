import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base" as Base
import "../../cores" as Cores
import "../../datas" as Datas
import "../../js/fmt.js" as Fmt
import "../../works" as Works

// TaskView presents the three-stage demo pipeline (capture/execute/control) using TaskDatas.
Base.BaseCard {
  id: root

  Layout.fillWidth: true
  implicitWidth: contentColumn.implicitWidth + 24
  implicitHeight: contentColumn.implicitHeight + 24

  readonly property var stageModel: [
    // Each entry maps to the corresponding TaskDatas payload and display metadata.
    ({ key: "capture", title: qsTr("采集任务"), subtitle: qsTr("3D图像采集 -> 算法处理"), readyFlag: "captureReady" }),
    ({ key: "execute", title: qsTr("执行任务"), subtitle: qsTr("路径执行"), readyFlag: "executeReady" }),
    ({ key: "control", title: qsTr("校验任务"), subtitle: qsTr("采集图像 -> 验证"), readyFlag: "controlReady" })
  ]

  function taskForKey(key) {
    switch (key) {
    case "capture":
      return Datas.TaskDatas.captureTask || {}
    case "execute":
      return Datas.TaskDatas.executeTask || {}
    case "control":
      return Datas.TaskDatas.controlTask || {}
    default:
      return {}
    }
  }

  function hasTask(task) {
    if (!task || typeof task !== "object")
      return false
    if (task.id !== undefined && task.id !== null)
      return true
    if (task.record_id !== undefined || task.recordId !== undefined)
      return true
    return false
  }

  function stageReady(stage) {
    if (!stage || !stage.readyFlag)
      return false
    var flag = stage.readyFlag
    if (Datas.TaskDatas.hasOwnProperty(flag))
      return !!Datas.TaskDatas[flag]
    return false
  }

  function statusText(task) {
    if (!hasTask(task))
      return qsTr("未下发")
    var value = task.status !== undefined ? task.status : task.statusText
    if (value === undefined || value === null || value === "")
      return qsTr("未知")
    var numeric = Number(value)
    if (!isNaN(numeric)) {
      switch (numeric) {
      case 0:
        return qsTr("排队中")
      case 1:
        return qsTr("执行中")
      case 2:
        return qsTr("已完成")
      case 3:
        return qsTr("失败")
      default:
        break
      }
    }
    var text = String(value).trim()
    if (!text.length)
      return qsTr("未知")
    var upper = text.toUpperCase()
    switch (upper) {
    case "PENDING":
    case "QUEUED":
      return qsTr("排队中")
    case "RUNNING":
      return qsTr("执行中")
    case "COMPLETED":
    case "DONE":
      return qsTr("已完成")
    case "FAILED":
    case "ERROR":
    case "FAULT":
      return qsTr("失败")
    default:
      return text
    }
  }

  function statusColor(task) {
    if (!hasTask(task))
      return Cores.CoreStyle.muted
    var value = task.status !== undefined ? task.status : task.statusText
    var numeric = Number(value)
    if (!isNaN(numeric)) {
      switch (numeric) {
      case 0:
        return Cores.CoreStyle.warning
      case 1:
        return Cores.CoreStyle.info
      case 2:
        return Cores.CoreStyle.success
      case 3:
        return Cores.CoreStyle.danger
      default:
        break
      }
    }
    var text = String(value || "").toUpperCase()
    if (text === "PENDING" || text === "QUEUED")
      return Cores.CoreStyle.warning
    if (text === "RUNNING")
      return Cores.CoreStyle.info
    if (text === "COMPLETED" || text === "DONE")
      return Cores.CoreStyle.success
    if (text === "FAILED" || text === "ERROR" || text === "FAULT")
      return Cores.CoreStyle.danger
    return Cores.CoreStyle.muted
  }

  function phaseText(task) {
    if (!hasTask(task))
      return "-"
    var detail = task.status_detail !== undefined ? task.status_detail : task.statusDetail
    if (!detail || typeof detail !== "object")
      detail = {}
    var phase = detail.phase !== undefined ? detail.phase : detail.state !== undefined ? detail.state : detail.stage
    if (!phase && detail.command)
      phase = detail.command
    if (phase)
      return Fmt.safeText(phase, "-")
    var payload = task.payload !== undefined ? task.payload : {}
    if (payload && typeof payload === "object" && payload.phase)
      return Fmt.safeText(payload.phase, "-")
    return "-"
  }

  function detailText(task) {
    if (!hasTask(task))
      return qsTr("尚未下发对应任务")
    var detail = task.status_detail !== undefined ? task.status_detail : {}
    var payload = task.payload !== undefined ? task.payload : {}
    var parts = []
    if (detail && detail.progress !== undefined)
      parts.push(qsTr("进度 %1%").arg(detail.progress))
    if (detail && detail.message)
      parts.push(qsTr("信息: %1").arg(Fmt.safeText(detail.message)))
    if (payload && payload.note)
      parts.push(qsTr("备注: %1").arg(Fmt.safeText(payload.note)))
    if (payload && payload.remark)
      parts.push(qsTr("备注: %1").arg(Fmt.safeText(payload.remark)))
    if (parts.length === 0) {
      var phase = phaseText(task)
      if (phase !== "-" && phase.length)
        parts.push(qsTr("阶段: %1").arg(phase))
    }
    return parts.length ? parts.join(" · ") : qsTr("暂无附加信息")
  }

  function recordText(task) {
    if (!hasTask(task))
      return "-"
    var recordId = pickField(task, ["record_id", "recordId"])
    if (recordId !== undefined && recordId !== null && recordId !== 0)
      return "#" + recordId
    return "-"
  }

  function taskIdText(task) {
    if (!hasTask(task))
      return "-"
    if (task.id !== undefined && task.id !== null)
      return "#" + task.id
    return "-"
  }

  function pickField(task, fields) {
    if (!task || typeof task !== "object")
      return undefined
    for (var i = 0; i < fields.length; ++i) {
      var key = fields[i]
      if (task[key] !== undefined && task[key] !== null && task[key] !== "")
        return task[key]
    }
    return undefined
  }

  function timeText(task, keys) {
    var candidate = pickField(task, keys)
    return candidate !== undefined ? Fmt.formatTimestamp(candidate) : "-"
  }

  function workpieceText() {
    var parts = []
    if (Datas.TaskDatas.workpieceCode && Datas.TaskDatas.workpieceCode !== "-")
      parts.push(Datas.TaskDatas.workpieceCode)
    if (Datas.TaskDatas.workpieceType && Datas.TaskDatas.workpieceType !== "-")
      parts.push(Datas.TaskDatas.workpieceType)
    if (!parts.length && Datas.TaskDatas.serialNumber && Datas.TaskDatas.serialNumber !== "-")
      parts.push(Datas.TaskDatas.serialNumber)
    return parts.length ? parts.join(" · ") : qsTr("未加载")
  }

  function currentRecordText() {
    var current = Cores.CoreCurrent.record || {}
    if (current.id)
      return "#" + current.id
    if (Datas.TaskDatas.latestRecordId)
      return "#" + Datas.TaskDatas.latestRecordId
    return "-"
  }

  Component.onCompleted: Works.TaskWork.start()

  Connections {
    target: Cores.CoreCurrent
    // Re-trigger polling when the selected record changes in CoreCurrent.
    function onRecordChanged() { Works.TaskWork.refresh() }
  }

  ColumnLayout {
    id: contentColumn
    anchors {
      fill: parent
      margins: 12
    }
    spacing: 16

    ColumnLayout {
      Layout.fillWidth: true
      spacing: 4

      Label {
        text: qsTr("任务流程")
        font.pixelSize: 20
        font.bold: true
        color: Cores.CoreStyle.text
      }

      RowLayout {
        Layout.fillWidth: true
        spacing: 12

        Label {
          text: qsTr("当前记录")
          color: Cores.CoreStyle.muted
        }

        Label {
          text: currentRecordText()
          color: Cores.CoreStyle.text
          font.bold: true
        }

        Item { Layout.fillWidth: true }

        Label {
          text: qsTr("工件")
          color: Cores.CoreStyle.muted
        }

        Label {
          text: workpieceText()
          color: Cores.CoreStyle.text
        }
      }
    }

    Repeater {
      model: stageModel

      delegate: Frame {
        Layout.fillWidth: true
        padding: 12
        background: Rectangle {
          color: "transparent"
          border.color: Cores.CoreStyle.border
          radius: 6
        }

        readonly property var stage: modelData
        readonly property var task: root.taskForKey(stage.key)
        readonly property bool available: root.hasTask(task)
        readonly property bool ready: root.stageReady(stage)

        ColumnLayout {
          anchors.fill: parent
          spacing: 8

          RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Rectangle {
              width: 28
              height: 28
              radius: 14
              color: Cores.CoreStyle.primary
              Label {
                anchors.centerIn: parent
                text: String(index + 1)
                color: "white"
                font.bold: true
              }
            }

            ColumnLayout {
              spacing: 2

              Label {
                text: stage.title
                color: Cores.CoreStyle.text
                font.pixelSize: 18
                font.bold: true
              }

              Label {
                text: stage.subtitle
                color: Cores.CoreStyle.muted
                wrapMode: Text.WordWrap
              }
            }

            Item { Layout.fillWidth: true }

            Label {
              text: ready ? qsTr("就绪") : qsTr("等待")
              color: ready ? Cores.CoreStyle.success : Cores.CoreStyle.warning
              font.bold: true
            }
          }

          RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Label {
              text: qsTr("任务状态")
              color: Cores.CoreStyle.muted
            }

            Label {
              text: root.statusText(task)
              color: root.statusColor(task)
              font.bold: true
            }

            Item { Layout.fillWidth: true }

            Label {
              text: qsTr("任务 ID")
              color: Cores.CoreStyle.muted
            }

            Label {
              text: root.taskIdText(task)
              color: Cores.CoreStyle.text
            }

            Label {
              text: qsTr("记录")
              color: Cores.CoreStyle.muted
            }

            Label {
              text: root.recordText(task)
              color: Cores.CoreStyle.text
            }
          }

          RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Label {
              text: qsTr("阶段")
              color: Cores.CoreStyle.muted
            }

            Label {
              text: root.phaseText(task)
              color: Cores.CoreStyle.text
              Layout.fillWidth: true
              wrapMode: Text.NoWrap
              elide: Text.ElideRight
            }

            Label {
              text: qsTr("创建时间")
              color: Cores.CoreStyle.muted
            }

            Label {
              text: available ? root.timeText(task, ["created_time", "createdTime", "queued_at", "queuedAt"]) : "-"
              color: Cores.CoreStyle.text
            }

            Label {
              text: qsTr("更新时间")
              color: Cores.CoreStyle.muted
            }

            Label {
              text: available ? root.timeText(task, ["updated_time", "updatedTime", "finished_at", "finishedAt", "status_time", "statusTime"]) : "-"
              color: Cores.CoreStyle.text
            }
          }

          Label {
            Layout.fillWidth: true
            text: root.detailText(task)
            color: available ? Cores.CoreStyle.muted : Cores.CoreStyle.muted
            wrapMode: Text.WordWrap
          }
        }
      }
    }
  }
}
