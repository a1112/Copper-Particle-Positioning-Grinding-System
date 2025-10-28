import QtQuick
import "../../cores" as Cores
import "../../datas" as Datas
import "../../works" as Works
import "../../Api" as Api
Item {
    id:root
    property bool refreshing: false
    property bool resetting: false
    property string actionMessage: ""
    property int alarmResetLevel: 3

    readonly property var captureTask: safeTask(Datas.TaskDatas.captureTask)
    readonly property var executeTask: safeTask(Datas.TaskDatas.executeTask)
    readonly property var controlTask: safeTask(Datas.TaskDatas.controlTask)
    readonly property var readyState: safeTask(Datas.TaskDatas.readyState)
    readonly property var statusSnapshot: statusPayload()

    property var commandModel: []
    property var alarmModel: []
    property var imageModel: []
    property var pathModel: []

    function refreshData() {
      Works.TaskWork.refresh()
      refreshAlarms()
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
        refreshAlarms()
      }, function(status, message) {
        refreshing = false
               showAction(qsTr("刷新失败: %1").arg(message || status))
        refreshAlarms()
      })
    }

    function resetAlarms() {
      if (resetting)
        return
      resetting = true
      var recordId = Datas.TaskDatas.latestRecordId || 0
      function finalize(message) {
        resetting = false
        if (message)
          showAction(message)
        refreshAlarms()
      }
      Api.ApiClient.control("reset", {}, function(resp) {
        var successMessage = qsTr("复位命令已下发")
        if (resp && resp.status)
          console.debug("reset response", resp)
        if (recordId > 0) {
          Api.ApiClient.post("/data/records/" + recordId + "/alarms/reset", { handler: "operator" }, function(_) {
            finalize(successMessage)
          }, function(status, message) {
            finalize(qsTr("\u62a5\u8b66\u72b6\u6001\u672a\u66f4\u65b0: %1").arg(message || status))
          })
        } else {
          finalize(successMessage)
        }
      }, function(status, message) {
        finalize(qsTr("复位失败: %1").arg(message || status))
      })
    }
    function refreshAlarms() {
      var recordId = Datas.TaskDatas.latestRecordId || 0
      if (!recordId) {
        applyAlarmResponse({ alarms: [], max_level: 0, requires_reset: false })
        return
      }
      Api.ApiClient.get("/data/records/" + recordId + '/alarms', function(resp) {
        applyAlarmResponse(resp || {})
      }, function(status, message) {
        console.warn('AlarmPanel refresh failed', status, message)
        applyAlarmResponse({ alarms: [], max_level: 0, requires_reset: false })
      })
    }

    function applyAlarmResponse(payload) {
      var alarms = (payload && payload.alarms) ? payload.alarms : []
      var mapped = []
      normalizeArray(alarms).forEach(function(item) {
        mapped.push(buildAlarmRow(item))
      })
      alarmModel = mapped
      var maxLevel = Number(payload && (payload.max_level !== undefined ? payload.max_level : payload.maxLevel))
      if (isNaN(maxLevel))
        maxLevel = 0
      Datas.TaskDatas.alarmMaxLevel = maxLevel
      Datas.TaskDatas.alarmLocked = !!(payload && (payload.requires_reset || payload.requiresReset))
    }

    function buildAlarmRow(entry) {
      if (!entry)
        return {}
      var code = safeText(readValue(entry, ['code', 'alarm_code']), '')
      var message = safeText(readValue(entry, ['message', 'alarm_message']), '-')
      var source = safeText(readValue(entry, ['type', 'alarm_type']), '')
      var levelValue = Number(readValue(entry, ['level', 'alarm_level']))
      if (isNaN(levelValue))
        levelValue = 0
      var handledStatus = Number(readValue(entry, ['handled_status', 'status']))
      if (isNaN(handledStatus))
        handledStatus = 0
      var handled = handledStatus >= 2
      var timestamp = readValue(entry, ['alarm_time', 'time', 'timestamp', 'created_time'])
      var handler = safeText(readValue(entry, ['handler', 'operator', 'handled_by']), '')
      return {
        id: readValue(entry, ['id']) || 0,
        recordId: readValue(entry, ['record_id']) || Datas.TaskDatas.latestRecordId,
        code: code,
        message: message,
        source: source,
        level: levelValue,
        levelText: alertLevelText(levelValue),
        tone: alertLevelColor(levelValue),
        timestamp: formatTimestamp(timestamp),
        handler: handler,
        handled: handled,
        statusText: handled ? qsTr('已处理') : (handledStatus === 1 ? qsTr('处理中') : qsTr('未处理')),
        statusTone: handled ? Cores.CoreStyle.success : (levelValue >= alarmResetLevel ? Cores.CoreStyle.danger : Cores.CoreStyle.warning)
      }
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
      parts.push(qsTr("采集: %1").arg(Datas.TaskDatas.captureReady ? qsTr("就绪华") : qsTr("等待緟")))
      parts.push(qsTr("执行: %1").arg(Datas.TaskDatas.executeReady ? qsTr("就绪华") : qsTr("等待緟")))
      parts.push(qsTr("控制: %1").arg(Datas.TaskDatas.controlReady ? qsTr("就绪华") : qsTr("等待緟")))
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
        return qsTr("未知")
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

      normalizeArray(Datas.TaskDatas.controlCommands).forEach(function(cmd) { appendEntry(cmd, qsTr('浠诲姟鎸囦护')); })
      return rows
    }

    function alertLevelColor(level) {
      if (level === undefined || level === null)
        return Cores.CoreStyle.muted
      var numeric = Number(level)
      if (!isNaN(numeric)) {
        if (numeric >= alarmResetLevel)
          return Cores.CoreStyle.danger
        if (numeric >= 2)
          return Cores.CoreStyle.warning
        if (numeric >= 1)
          return Cores.CoreStyle.info
        return Cores.CoreStyle.muted
      }
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
      var numeric = Number(level)
      if (!isNaN(numeric)) {
        if (numeric >= alarmResetLevel)
          return qsTr('报警')
        if (numeric >= 2)
          return qsTr('预警')
        if (numeric >= 1)
          return qsTr('提示')
        return qsTr('通知')
      }
      var upper = String(level || "").toUpperCase()
      switch (upper) {
      case "ERROR":
      case "FAULT":
      case "CRITICAL":
        return qsTr('报警')
      case "WARN":
      case "WARNING":
        return qsTr('预警')
      case "INFO":
      case "NOTICE":
        return qsTr('提示')
      default:
        return safeText(level, qsTr('未知'))
      }
    }
    function rebuildDerived() {
      commandModel = buildCommandModel()
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
      function onLatestRecordIdChanged() { refreshAlarms() }
    }
}
