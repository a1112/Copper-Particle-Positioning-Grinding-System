import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../cores" as Cores
import "../../datas" as Datas
import "../../works" as Works
import "../../Api" as Api

Popup {
  id: root
  modal: true
  dim: true
  focus: true
  padding: 0
  anchors.centerIn: parent
  width: parent ? Math.min(parent.width * 0.85, 1480) : 1180
  height: parent ? Math.min(parent.height * 0.9, 860) : 680
  closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

  property bool refreshing: false
  property bool resetting: false
  property string actionMessage: ""

  readonly property var captureTask: safeTask(Datas.TaskDatas.captureTask)
  readonly property var executeTask: safeTask(Datas.TaskDatas.executeTask)
  readonly property var controlTask: safeTask(Datas.TaskDatas.controlTask)
  readonly property var readyState: safeTask(Datas.TaskDatas.readyState)
  readonly property var statusSnapshot: statusPayload()

  property var commandModel: []
  property var alertModel: []
  property var imageModel: []
  property var pathModel: []

  background: Rectangle {
    radius: 14
    color: Cores.CoreStyle.surface
    border.color: Cores.CoreStyle.border
    border.width: 1
  }

  Component.onCompleted: refreshData()
  onOpened: refreshData()

  function refreshData() {
    Works.TaskWork.refresh()
    refreshing = true
    Api.ApiClient.status(function(payload) {
      refreshing = false
      try {
        if (payload)
          Datas.StatusDatas.ingest(payload)
        rebuildDerived()
        showAction(qsTr("状态已刷新"))
      } catch (err) {
        console.warn("StatePage ingest failed", err)
      }
    }, function(status, message) {
      refreshing = false
      showAction(qsTr("刷新失败: %1").arg(message || status))
    })
  }

  function resetAlarms() {
    if (resetting)
      return
    resetting = true
    Api.ApiClient.control("reset", {}, function(resp) {
      resetting = false
      showAction(qsTr("复位命令已下发"))
      if (resp && resp.status)
        console.debug("reset response", resp)
    }, function(status, message) {
      resetting = false
      showAction(qsTr("复位失败: %1").arg(message || status))
    })
  }

  function showAction(text) {
    actionMessage = text || ""
    actionTimer.restart()
  }

  Timer {
    id: actionTimer
    interval: 4000
    repeat: false
    onTriggered: root.actionMessage = ""
  }

  function statusPayload() {
    var payload = Datas.StatusDatas.lastMessage
    if (payload === undefined || payload === null)
      payload = {}
    return payload
  }

  function safeTask(task) {
    if (task === undefined || task === null)
      return {}
    if (typeof task !== "object")
      return {}
    return task
  }

  function safeText(value, fallback) {
    if (value === undefined || value === null)
      return fallback !== undefined ? fallback : "-"
    var text = String(value).trim()
    if (text.length === 0)
      return fallback !== undefined ? fallback : "-"
    return text
  }

  function asNumber(value) {
    if (value === undefined || value === null || value === "")
      return undefined
    var num = Number(value)
    return isNaN(num) ? undefined : num
  }

  function formatTimestamp(value) {
    if (value === undefined || value === null || value === "")
      return "-"
    if (value instanceof Date)
      return Qt.formatDateTime(value, "yyyy-MM-dd hh:mm:ss")
    if (typeof value === "number") {
      var ms = value
      if (ms < 2000000000)
        ms = ms * 1000
      return Qt.formatDateTime(new Date(ms), "yyyy-MM-dd hh:mm:ss")
    }
    var parsed = Date.parse(value)
    if (!isNaN(parsed))
      return Qt.formatDateTime(new Date(parsed), "yyyy-MM-dd hh:mm:ss")
    return safeText(value, "-")
  }

  function currentSerial() {
    var direct = statusSnapshot.serial_number || statusSnapshot.serialNumber
    if (direct)
      return safeText(direct, "-")
    if (Datas.TaskDatas.serialNumber && Datas.TaskDatas.serialNumber !== "-")
      return Datas.TaskDatas.serialNumber
    return Datas.TaskDatas.workpieceCode || "-"
  }

  function workpieceLabel() {
    var code = safeText(Datas.TaskDatas.workpieceCode, "-")
    var type = safeText(Datas.TaskDatas.workpieceType, "-")
    return code + " · " + type
  }

  function readySummary() {
    var parts = []
    parts.push(qsTr("采集: %1").arg(Datas.TaskDatas.captureReady ? qsTr("就绪") : qsTr("等待")))
    parts.push(qsTr("执行: %1").arg(Datas.TaskDatas.executeReady ? qsTr("就绪") : qsTr("等待")))
    parts.push(qsTr("控制: %1").arg(Datas.TaskDatas.controlReady ? qsTr("就绪") : qsTr("等待")))
    return parts.join(" | ")
  }

  function taskStatusText(value) {
    if (value === undefined || value === null || value === "")
      return qsTr("未知")
    var code = Number(value)
    if (!isNaN(code)) {
      switch (code) {
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

  function statusColor(value) {
    var code = Number(value)
    if (!isNaN(code)) {
      switch (code) {
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
    if (text === "PENDING")
      return Cores.CoreStyle.warning
    if (text === "RUNNING")
      return Cores.CoreStyle.info
    if (text === "COMPLETED" || text === "DONE")
      return Cores.CoreStyle.success
    if (text === "FAILED" || text === "ERROR" || text === "FAULT")
      return Cores.CoreStyle.danger
    if (text === "WARNING")
      return Cores.CoreStyle.warning
    return Cores.CoreStyle.muted
  }

  function phaseText(task) {
    var detail = task && task.status_detail ? task.status_detail : task && task.statusDetail ? task.statusDetail : {}
    var phase = detail.phase || detail.state || detail.stage
    return phase ? safeText(phase, "-") : "-"
  }

  function detailText(task) {
    var detail = task && task.status_detail ? task.status_detail : {}
    var payload = task && task.payload ? task.payload : {}
    var parts = []
    if (detail.progress !== undefined)
      parts.push(qsTr("进度 %1%").arg(detail.progress))
    if (detail.message)
      parts.push(safeText(detail.message))
    if (payload.note)
      parts.push(qsTr("备注: %1").arg(safeText(payload.note)))
    if (parts.length === 0 && phaseText(task) !== "-")
      parts.push(qsTr("阶段: %1").arg(phaseText(task)))
    return parts.length ? parts.join(" · ") : qsTr("暂无补充信息")
  }

  function normalizeArray(value) {
    if (value === undefined || value === null)
      return []
    if (Array.isArray(value))
      return value
    if (typeof value === "string")
      return [value]
    if (typeof value === "object") {
      if (Array.isArray(value.items))
        return value.items
      if (Array.isArray(value.list))
        return value.list
      return [value]
    }
    return []
  }

  function readValue(source, keys) {
    if (!source)
      return undefined
    for (var i = 0; i < keys.length; ++i) {
      var key = keys[i]
      if (source[key] !== undefined)
        return source[key]
    }
    return undefined
  }

  function displacementText(row) {
    var parts = []
    if (row.ex !== undefined)
      parts.push("X " + row.ex.toFixed(3))
    if (row.ey !== undefined)
      parts.push("Y " + row.ey.toFixed(3))
    if (row.ez !== undefined)
      parts.push("Z " + row.ez.toFixed(3))
    return parts.length ? parts.join("  ") : "-"
  }

  function asFileUrl(path) {
    if (path === undefined || path === null)
      return ""
    var text = String(path)
    if (!text.length)
      return ""
    if (text.indexOf("file:") === 0)
      return text
    var normalised = text.replace(/\\/g, "/")
    if (normalised.length >= 2 && normalised.charAt(1) === ":")
      normalised = normalised.charAt(0) + ":" + normalised.substring(1)
    if (normalised.charAt(0) === "/")
      return "file://" + normalised
    return "file:///" + normalised
  }

  function coerceNumber(value, fallback) {
    if (value === undefined || value === null || value === "")
      return fallback
    var num = Number(value)
    return isNaN(num) ? fallback : num
  }

  function buildImageModel() {
    var rows = []
    var payload = Datas.TaskDatas.gcodeData || {}
    var images = payload.image_files || payload.images || {}
    if (Array.isArray(images)) {
      images.forEach(function(item, index) {
        var path = typeof item === "string" ? item : (item && item.path)
        if (!path)
          return
        rows.push({
          title: item && item.title ? safeText(item.title, qsTr("图像 %1").arg(index + 1)) : qsTr("图像 %1").arg(index + 1),
          path: safeText(path, ""),
          url: asFileUrl(path),
        })
      })
    } else if (typeof images === "object") {
      var mapping = [
        { key: "color", title: qsTr("彩色") },
        { key: "gray", title: qsTr("灰度") },
        { key: "depth", title: qsTr("深度") },
        { key: "normal", title: qsTr("法线") },
      ]
      for (var i = 0; i < mapping.length; ++i) {
        var entry = mapping[i]
        var val = images[entry.key]
        if (!val)
          continue
        var rel = typeof val === "object" && val.path ? val.path : val
        rows.push({
          title: entry.title,
          path: safeText(rel, ""),
          url: asFileUrl(rel),
        })
      }
      for (var key in images) {
        if (!images.hasOwnProperty(key))
          continue
        var hasNamed = mapping.some(function(m) { return m.key === key })
        if (hasNamed)
          continue
        var extra = images[key]
        if (!extra)
          continue
        var extraPath = typeof extra === "object" && extra.path ? extra.path : extra
        rows.push({
          title: safeText(key, qsTr("图像")),
          path: safeText(extraPath, ""),
          url: asFileUrl(extraPath),
        })
      }
    }
    return rows
  }

  function buildPathModel() {
    var rows = []
    var payload = Datas.TaskDatas.gcodeData || {}
    var preview = payload.path_preview || payload.pathPreview || payload.commands
    var list = normalizeArray(preview)
    if (!list.length && Array.isArray(payload.commands))
      list = payload.commands
    normalizeArray(list).forEach(function(item, index) {
      if (item === undefined || item === null)
        return
      var row = {}
      if (typeof item === "object") {
        row.index = coerceNumber(readValue(item, ["index", "sequence", "id", "step"]), index + 1)
        row.x = coerceNumber(readValue(item, ["x", "ex", "target_x", "offset_x"]), undefined)
        row.y = coerceNumber(readValue(item, ["y", "ey", "target_y", "offset_y"]), undefined)
        row.z = coerceNumber(readValue(item, ["z", "ez", "target_z", "offset_z"]), undefined)
        row.velocity = coerceNumber(readValue(item, ["velocity", "feed", "v", "feed_rate"]), undefined)
        row.command = safeText(readValue(item, ["command", "cmd", "name", "action"]), "")
      } else {
        row.index = index + 1
        row.command = safeText(item, "")
      }
      row.indexText = row.index !== undefined ? row.index : index + 1
      row.positionText = ""
      var coords = []
      if (row.x !== undefined)
        coords.push("X " + Number(row.x).toFixed(3))
      if (row.y !== undefined)
        coords.push("Y " + Number(row.y).toFixed(3))
      if (row.z !== undefined)
        coords.push("Z " + Number(row.z).toFixed(3))
      if (coords.length)
        row.positionText = coords.join("  ")
      row.velocityText = row.velocity !== undefined ? Number(row.velocity).toFixed(2) : "-"
      if (!row.command && coords.length)
        row.command = coords.join(" ")
      rows.push(row)
    })
    return rows
  }

  function buildCommandModel() {
    var rows = []
    var seq = 1
    function appendEntry(entry, sourceLabel) {
      if (entry === undefined || entry === null)
        return
      var row = {
        sequence: seq++,
        source: sourceLabel || '-',
        id: undefined
      }
      if (typeof entry === 'string') {
        row.commandText = safeText(entry, '-')
      } else if (typeof entry === 'object') {
        row.id = readValue(entry, ['id', 'task_id', 'taskId']) || row.id
        row.sequence = readValue(entry, ['sequence', 'seq', 'order', 'index', 'step']) || row.sequence
        row.commandText = safeText(
              readValue(entry, ['command', 'cmd', 'command_text', 'text', 'instruction', 'display', 'action', 'name']),
              '-'
            )
        var payload = entry.payload && typeof entry.payload === 'object' ? entry.payload : entry
        row.ex = asNumber(readValue(payload, ['ex', 'dx', 'offset_x', 'offsetX', 'x']))
        row.ey = asNumber(readValue(payload, ['ey', 'dy', 'offset_y', 'offsetY', 'y']))
        row.ez = asNumber(readValue(payload, ['ez', 'dz', 'offset_z', 'offsetZ', 'z', 'depth']))
        row.rpm = asNumber(readValue(payload, ['spindle_rpm', 'rpm', 'r', 'speed_rpm']))
        row.velocity = asNumber(readValue(payload, ['velocity', 'feed', 'feed_rate', 'feedRate', 'v']))
        row.statusRaw = readValue(entry, ['status', 'state', 'phase', 'result'])
        row.timestampRaw = readValue(entry, ['timestamp', 'ts', 'time', 'created_time', 'updated_time'])
        row.message = safeText(readValue(entry, ['message', 'msg', 'detail', 'note']), '')
        row.source = safeText(readValue(entry, ['source', 'origin', 'from']), row.source)
        if (!row.commandText || row.commandText === '-')
          row.commandText = safeText(readValue(payload, ['action', 'command']), '-')
      } else {
        row.commandText = safeText(entry, '-')
      }
      if (row.id === undefined)
        row.id = row.sequence
      if (row.id !== undefined)
        row.sequence = row.id
      row.statusText = row.statusRaw ? taskStatusText(row.statusRaw) : '-'
      row.statusTone = statusColor(row.statusRaw)
      row.timestamp = formatTimestamp(row.timestampRaw)
      rows.push(row)
    }

    normalizeArray(Datas.TaskDatas.controlCommands).forEach(function(cmd) { appendEntry(cmd, qsTr('任务指令')); })
    return rows
  }

  function alertLevelColor(level) {
    var upper = String(level || "").toUpperCase()
    switch (upper) {
    case "ERROR":
    case "FAULT":
    case "CRITICAL":
      return Cores.CoreStyle.danger
    case "WARN":
    case "WARNING":
      return Cores.CoreStyle.warning
    case "INFO":
    case "NOTICE":
      return Cores.CoreStyle.info
    default:
      return Cores.CoreStyle.muted
    }
  }

  function alertLevelText(level) {
    var upper = String(level || "").toUpperCase()
    switch (upper) {
    case "ERROR":
    case "FAULT":
    case "CRITICAL":
      return qsTr("报警")
    case "WARN":
    case "WARNING":
      return qsTr("预警")
    case "INFO":
    case "NOTICE":
      return qsTr("提示")
    default:
      return safeText(level, qsTr("未知"))
    }
  }

  function buildAlertModel() {
    var rows = []
    var keys = ["alerts", "alarms", "alarm_list", "alarmList", "warnings", "errors", "messages"]
    for (var i = 0; i < keys.length; ++i) {
      var key = keys[i]
      var list = statusSnapshot[key]
      normalizeArray(list).forEach(function(entry) {
        var row = {}
        if (typeof entry === "string") {
          row.message = safeText(entry, "-")
          row.level = "INFO"
        } else if (typeof entry === "object") {
          row.level = readValue(entry, ["level", "severity", "type"]) || "INFO"
          row.message = safeText(readValue(entry, ["message", "msg", "detail", "description", "text"]), "-")
          row.code = safeText(readValue(entry, ["code", "fault", "id"]), "")
          row.timestamp = formatTimestamp(readValue(entry, ["timestamp", "ts", "time"]))
          row.source = safeText(readValue(entry, ["source", "origin"]), "")
        }
        if (!row.message)
          row.message = "-"
        row.levelText = alertLevelText(row.level)
        row.tone = alertLevelColor(row.level)
        if (!row.timestamp)
          row.timestamp = formatTimestamp(statusSnapshot.status_time)
        rows.push(row)
      })
    }
    var faultCode = statusSnapshot.fault_code || statusSnapshot.faultCode
    var faultMessage = statusSnapshot.fault_message || statusSnapshot.faultMessage
    if (faultCode || faultMessage) {
      rows.push({
        level: "ERROR",
        levelText: alertLevelText("ERROR"),
        tone: alertLevelColor("ERROR"),
        code: safeText(faultCode, ""),
        message: safeText(faultMessage, qsTr("控制器报告设备故障")),
        timestamp: formatTimestamp(statusSnapshot.status_time),
        source: "StatusTable"
      })
    }
    if (!rows.length && String(statusSnapshot.state || "").toUpperCase() === "FAULT") {
      rows.push({
        level: "ERROR",
        levelText: alertLevelText("ERROR"),
        tone: alertLevelColor("ERROR"),
        message: qsTr("设备处于故障状态"),
        timestamp: formatTimestamp(statusSnapshot.status_time || Date.now()),
        source: "Controller"
      })
    }
    return rows
  }

  function rebuildDerived() {
    commandModel = buildCommandModel()
    alertModel = buildAlertModel()
    imageModel = buildImageModel()
    pathModel = buildPathModel()
  }

  Connections {
    target: Datas.StatusDatas
    function onMessageReceived(_) {
      root.rebuildDerived()
    }
  }

  Connections {
    target: Datas.TaskDatas
    function onCaptureTaskChanged() { root.rebuildDerived() }
    function onExecuteTaskChanged() { root.rebuildDerived() }
    function onControlTaskChanged() { root.rebuildDerived() }
    function onReadyStateChanged() { root.rebuildDerived() }
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 24
    spacing: 16

    RowLayout {
      Layout.fillWidth: true
      Label {
        text: qsTr("指令状态与报警中心")
        font.pixelSize: 22
        font.bold: true
        color: Cores.CoreStyle.text
        Layout.alignment: Qt.AlignVCenter
      }
      Label {
        text: qsTr("流水号 %1 · %2").arg(currentSerial()).arg(readySummary())
        color: Cores.CoreStyle.muted
        elide: Text.ElideRight
        Layout.alignment: Qt.AlignVCenter
        Layout.fillWidth: true
      }
      Button {
        text: refreshing ? qsTr("刷新中...") : qsTr("刷新")
        enabled: !refreshing
        Layout.alignment: Qt.AlignVCenter
        onClicked: refreshData()
      }
      Button {
        text: qsTr("关闭")
        Layout.alignment: Qt.AlignVCenter
        onClicked: root.close()
      }
    }

    Rectangle {
      Layout.fillWidth: true
      radius: 10
      color: "#131c2b"
      border.color: "#1f2a3b"
      anchors.margins: 0
      RowLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 24

        ColumnLayout {
          spacing: 4
          Label { text: qsTr("工件信息"); color: Cores.CoreStyle.muted; font.pixelSize: 12 }
          Label { text: workpieceLabel(); color: Cores.CoreStyle.text; font.pixelSize: 18; font.bold: true }
        }

        ColumnLayout {
          spacing: 4
          Label { text: qsTr("最新记录ID"); color: Cores.CoreStyle.muted; font.pixelSize: 12 }
          Label { text: Datas.TaskDatas.latestRecordId ? ("#" + Datas.TaskDatas.latestRecordId) : "-"; color: Cores.CoreStyle.text; font.pixelSize: 18; font.bold: true }
        }

        ColumnLayout {
          spacing: 4
          Label { text: qsTr("状态"); color: Cores.CoreStyle.muted; font.pixelSize: 12 }
          Label { text: safeText(statusSnapshot.state, qsTr("待机")); color: statusColor(statusSnapshot.state); font.pixelSize: 18; font.bold: true }
        }

        ColumnLayout {
          spacing: 4
          Label { text: qsTr("运行模式"); color: Cores.CoreStyle.muted; font.pixelSize: 12 }
          Label { text: safeText(statusSnapshot.run_mode || statusSnapshot.runMode, "-"); color: Cores.CoreStyle.info; font.pixelSize: 18; font.bold: true }
        }

        Item { Layout.fillWidth: true }
      }
    }

    TabBar {
      id: tabBar
      Layout.fillWidth: true
      TabButton { text: qsTr("控制指令状态") }
      TabButton { text: qsTr("报警处理") }
    }

    StackLayout {
      Layout.fillWidth: true
      Layout.fillHeight: true
      currentIndex: tabBar.currentIndex

      Item {
        Layout.fillWidth: true
        Layout.fillHeight: true
        ScrollView {
          anchors.fill: parent
          clip: true
          ScrollBar.vertical.policy: ScrollBar.AsNeeded
          contentItem: Flickable {
            id: commandFlick
            clip: true
            contentWidth: width
            contentHeight: commandColumn.implicitHeight
            boundsBehavior: Flickable.StopAtBounds
            ColumnLayout {
              id: commandColumn
              width: commandFlick.width - 12
              spacing: 20

            ColumnLayout {
              Layout.fillWidth: true
              spacing: 12

              Label {
                text: qsTr("任务队列")
                font.pixelSize: 18
                font.bold: true
                color: Cores.CoreStyle.text
              }

              Repeater {
                model: [
                  ({ title: qsTr("采集任务"), desc: qsTr("等待算法生成控制指令"), task: captureTask, ready: Datas.TaskDatas.captureReady }),
                  ({ title: qsTr("执行任务"), desc: qsTr("下发执行流程控制指令"), task: executeTask, ready: Datas.TaskDatas.executeReady }),
                  ({ title: qsTr("控制任务"), desc: qsTr("驱动层控制指令队列"), task: controlTask, ready: Datas.TaskDatas.controlReady })
                ]

                delegate: ColumnLayout {
                  Layout.fillWidth: true
                  spacing: 6

                  Label {
                    text: modelData.title + " · " + (modelData.ready ? qsTr("就绪") : qsTr("等待"))
                    font.pixelSize: 16
                    font.bold: true
                    color: modelData.ready ? Cores.CoreStyle.success : Cores.CoreStyle.warning
                  }

                  Rectangle {
                    Layout.fillWidth: true
                    radius: 8
                    color: "#111a28"
                    border.color: "#1d2a3f"

                    ColumnLayout {
                      anchors.fill: parent
                      anchors.margins: 14
                      spacing: 10

                      RowLayout {
                        Layout.fillWidth: true
                        spacing: 18
                        Label { text: qsTr("状态"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 80 }
                        Label {
                          text: taskStatusText(modelData.task.status)
                          color: statusColor(modelData.task.status)
                          font.pixelSize: 15
                          font.bold: true
                        }
                        Label { text: qsTr("阶段"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 80 }
                        Label {
                          text: phaseText(modelData.task)
                          color: Cores.CoreStyle.text
                          Layout.fillWidth: true
                        }
                      }

                      RowLayout {
                        Layout.fillWidth: true
                        spacing: 18
                        Label { text: qsTr("创建时间"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 80 }
                        Label {
                          text: formatTimestamp(modelData.task.created_time || modelData.task.createdTime)
                          color: Cores.CoreStyle.text
                          Layout.fillWidth: true
                        }
                        Label { text: qsTr("更新"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 60 }
                        Label {
                          text: formatTimestamp(modelData.task.updated_time || modelData.task.updatedTime)
                          color: Cores.CoreStyle.text
                          Layout.fillWidth: true
                        }
                      }

                      Label {
                        text: detailText(modelData.task)
                        color: Cores.CoreStyle.muted
                        wrapMode: Text.Wrap
                      }
                    }
                  }
                }
              }
            }

            ColumnLayout {
              Layout.fillWidth: true
              spacing: 10

              RowLayout {
                Layout.fillWidth: true
                spacing: 10
                Label {
                  text: qsTr('任务指令列表')
                  font.pixelSize: 18
                  font.bold: true
                  color: Cores.CoreStyle.text
                }
                Item { Layout.fillWidth: true }
                Button {
                  text: qsTr('清空指令')
                  enabled: commandModel.length > 0 && Datas.StatusDatas.controlEnabled
                  onClicked: Works.TaskWork.clearCommands()
                }
                Label {
                  text: commandModel.length ? qsTr('共 %1 条').arg(commandModel.length) : qsTr('暂无指令')
                  color: Cores.CoreStyle.muted
                }
              }

              Rectangle {
                Layout.fillWidth: true
                radius: 6
                color: "#172033"
                border.color: "#1f2c44"
                height: headerRow.implicitHeight + 12
                RowLayout {
                  id: headerRow
                  anchors.fill: parent
                  anchors.margins: 8
                  spacing: 12
                  Label { text: qsTr('序号'); color: Cores.CoreStyle.muted; Layout.preferredWidth: 60 }
                  Label { text: qsTr('指令'); color: Cores.CoreStyle.muted; Layout.fillWidth: true }
                  Label { text: qsTr('位移(mm)'); color: Cores.CoreStyle.muted; Layout.preferredWidth: 140 }
                  Label { text: qsTr('转速'); color: Cores.CoreStyle.muted; Layout.preferredWidth: 90 }
                  Label { text: qsTr('进给'); color: Cores.CoreStyle.muted; Layout.preferredWidth: 90 }
                  Label { text: qsTr('状态'); color: Cores.CoreStyle.muted; Layout.preferredWidth: 100 }
                  Label { text: qsTr('时间'); color: Cores.CoreStyle.muted; Layout.preferredWidth: 160 }
                  Label { text: qsTr('备注'); color: Cores.CoreStyle.muted; Layout.preferredWidth: 180 }
                  Label { text: qsTr('操作'); color: Cores.CoreStyle.muted; Layout.preferredWidth: 80 }
                }

              Repeater {
                model: commandModel
                delegate: Rectangle {
                  Layout.fillWidth: true
                  radius: 4
                  color: index % 2 === 0 ? "#101725" : "#0d1421"
                  border.color: "#182133"
                  height: contentRow.implicitHeight + 10

                  RowLayout {
                    id: contentRow
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 12

                    Label { text: modelData.sequence; color: Cores.CoreStyle.text; Layout.preferredWidth: 60 }
                    Label {
                      text: modelData.commandText
                      color: Cores.CoreStyle.text
                      wrapMode: Text.Wrap
                      Layout.fillWidth: true
                    }
                    Label {
                      text: displacementText(modelData)
                      color: Cores.CoreStyle.text
                      Layout.preferredWidth: 140
                      wrapMode: Text.Wrap
                    }
                    Label {
                      text: modelData.rpm !== undefined ? modelData.rpm.toFixed(1) : "-"
                      color: Cores.CoreStyle.text
                      Layout.preferredWidth: 90
                    }
                    Label {
                      text: modelData.velocity !== undefined ? modelData.velocity.toFixed(2) : "-"
                      color: Cores.CoreStyle.text
                      Layout.preferredWidth: 90
                    }
                    Label {
                      text: modelData.statusText
                      color: modelData.statusTone
                      font.bold: true
                      Layout.preferredWidth: 100
                    }
                    Label {
                      text: modelData.timestamp
                      color: Cores.CoreStyle.muted
                      Layout.preferredWidth: 160
                      wrapMode: Text.WrapAnywhere
                    }
                    Label {
                      text: modelData.message ? modelData.message : modelData.source
                      color: Cores.CoreStyle.muted
                      wrapMode: Text.Wrap
                      Layout.preferredWidth: 180
                    }
                    Button {
                      text: qsTr('删除')
                      enabled: Datas.StatusDatas.controlEnabled && modelData && modelData.id
                      Layout.preferredWidth: 80
                      onClicked: Works.TaskWork.deleteCommand(modelData.id)
                    }
                  }
                }
              }

              Label {
                visible: commandModel.length === 0
                text: qsTr("当前流水号暂无控制指令，请等待采集任务完成后再试。")
                color: Cores.CoreStyle.muted
              }

              ColumnLayout {
                Layout.fillWidth: true
                spacing: 10

                RowLayout {
                  Layout.fillWidth: true
                  spacing: 10
                  Label {
                    text: qsTr("采集图像预览")
                    font.pixelSize: 18
                    font.bold: true
                    color: Cores.CoreStyle.text
                  }
                  Item { Layout.fillWidth: true }
                  Label {
                    text: Datas.TaskDatas.latestRecordId ? qsTr("记录 #%1").arg(Datas.TaskDatas.latestRecordId) : "-"
                    color: Cores.CoreStyle.muted
                  }
                }

                Flow {
                  Layout.fillWidth: true
                  spacing: 14
                  Repeater {
                    model: imageModel
                    delegate: ColumnLayout {
                      width: Math.min(260, commandColumn.width / 3)
                      spacing: 6
                      Rectangle {
                        Layout.fillWidth: true
                        height: width * 0.75
                        radius: 8
                        color: "#0f1722"
                        border.color: "#1c2840"
                        clip: true
                        Image {
                          anchors.fill: parent
                          fillMode: Image.PreserveAspectFit
                          source: modelData.url
                        }
                      }
                      Label {
                        text: modelData.title
                        color: Cores.CoreStyle.text
                        font.bold: true
                      }
                      Label {
                        text: modelData.path
                        color: Cores.CoreStyle.muted
                        wrapMode: Text.WrapAnywhere
                      }
                    }
                  }
                  Label {
                    visible: imageModel.length === 0
                    text: qsTr("暂无采集图像，请先完成采集流程。")
                    color: Cores.CoreStyle.muted
                  }
                }
              }

              ColumnLayout {
                Layout.fillWidth: true
                spacing: 8

                RowLayout {
                  Layout.fillWidth: true
                  spacing: 10
                  Label {
                    text: qsTr("路径预览")
                    font.pixelSize: 18
                    font.bold: true
                    color: Cores.CoreStyle.text
                  }
                  Item { Layout.fillWidth: true }
                  Label {
                    text: pathModel.length ? qsTr("共 %1 段").arg(pathModel.length) : ""
                    color: Cores.CoreStyle.muted
                  }
                }

                Rectangle {
                  Layout.fillWidth: true
                  radius: 6
                  color: "#141d2e"
                  border.color: "#1f2c44"
                  ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 6
                    Repeater {
                      model: pathModel
                      delegate: RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        Label {
                          text: modelData.indexText
                          color: Cores.CoreStyle.info
                          font.bold: true
                          Layout.preferredWidth: 40
                        }
                        Label {
                          text: modelData.command
                          color: Cores.CoreStyle.text
                          Layout.fillWidth: true
                          wrapMode: Text.Wrap
                        }
                        Label {
                          text: modelData.positionText
                          color: Cores.CoreStyle.muted
                          Layout.preferredWidth: 220
                          wrapMode: Text.WrapAnywhere
                        }
                        Label {
                          text: modelData.velocityText
                          color: Cores.CoreStyle.muted
                          Layout.preferredWidth: 80
                        }
                      }
                    }
                    Label {
                      visible: pathModel.length === 0
                      text: qsTr("暂无路径信息，等待采集完成生成。")
                      color: Cores.CoreStyle.muted
                    }
                  }
                }
              }
            }
          }
        }
      }

      Item {
        Layout.fillWidth: true
        Layout.fillHeight: true
        ColumnLayout {
          anchors.fill: parent
          spacing: 14

          RowLayout {
            Layout.fillWidth: true
            Label {
              text: qsTr("报警列表")
              font.pixelSize: 18
              font.bold: true
              color: Cores.CoreStyle.text
            }
            Item { Layout.fillWidth: true }
            Button {
              text: resetting ? qsTr("复位中...") : qsTr("复位报警")
              enabled: !resetting
              onClicked: resetAlarms()
            }
          }

          ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.vertical.policy: ScrollBar.AsNeeded
            contentItem: Flickable {
              id: alertFlick
              clip: true
              contentHeight: alertColumn.implicitHeight
              contentWidth: width
              boundsBehavior: Flickable.StopAtBounds
              ColumnLayout {
                id: alertColumn
                width: alertFlick.width - 12
                spacing: 12

              Repeater {
                model: alertModel
                delegate: Rectangle {
                  Layout.fillWidth: true
                  radius: 8
                  color: "#131a27"
                  border.color: "#1d2535"

                  ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 6

                    RowLayout {
                      Layout.fillWidth: true
                      spacing: 10
                      Rectangle {
                        width: 10
                        height: 10
                        radius: 5
                        color: modelData.tone
                        border.color: modelData.tone
                      }
                      Label {
                        text: modelData.levelText
                        font.bold: true
                        color: modelData.tone
                      }
                      Label {
                        text: modelData.code && modelData.code !== "-" ? ("#" + modelData.code) : ""
                        color: Cores.CoreStyle.muted
                      }
                      Item { Layout.fillWidth: true }
                      Label {
                        text: modelData.timestamp
                        color: Cores.CoreStyle.muted
                      }
                    }

                    Label {
                      text: modelData.message
                      color: Cores.CoreStyle.text
                      wrapMode: Text.Wrap
                    }

                    Label {
                      text: modelData.source ? qsTr("来源: %1").arg(modelData.source) : ""
                      color: Cores.CoreStyle.muted
                    }
                  }
                }
              }

              Label {
                visible: alertModel.length === 0
                text: qsTr("当前无报警，设备运行正常。")
                color: Cores.CoreStyle.muted
                horizontalAlignment: Text.AlignHCenter
                Layout.fillWidth: true
              }
            }
          }

          Label {
            text: actionMessage
            color: Cores.CoreStyle.info
            visible: actionMessage.length > 0
          }
        }
      }
    }
  }

  BusyIndicator {
    anchors.centerIn: parent
    running: refreshing
    visible: refreshing
    z: 3
  }
}
}
}
