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
    property var runnerHealth: ({})
    property string lastRunnerAlertKey: ""

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
      if (value === "离线")
        return Cores.CoreStyle.danger
      var rawText = String(value || "")
      if (rawText === "离线")
        return Cores.CoreStyle.danger
      var text = rawText.toUpperCase()
      if (text === "OFFLINE" || text === "RUNNER_FAULT")
        return Cores.CoreStyle.danger
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

    function friendlyCommandName(action) {
      var mapping = {
        "capture": qsTr("采集"),
        "run.start": qsTr("开始执行"),
        "start": qsTr("开始执行"),
        "run.stop": qsTr("停止执行"),
        "stop": qsTr("停止执行"),
        "run.pause": qsTr("暂停"),
        "pause": qsTr("暂停"),
        "run.resume": qsTr("继续执行"),
        "resume": qsTr("继续执行"),
        "estop": qsTr("急停"),
        "reset": qsTr("复位"),
        "motion.set_speed": qsTr("设置速度"),
        "motion.set_work_origin": qsTr("设置工件原点"),
        "motion.home": qsTr("回零"),
        "motion.jog": qsTr("点动"),
        "boost": qsTr("性能提升"),
      }
      var key = String(action || "").toLowerCase()
      if (mapping[key] !== undefined)
        return mapping[key]
      if (!key.length)
        return qsTr("控制指令")
      return safeText(action, qsTr("控制指令"))
    }

    function formatJson(value) {
      if (value === undefined || value === null)
        return "-"
      if (typeof value === "string") {
        var trimmed = value.trim()
        return trimmed.length ? trimmed : "-"
      }
      if (typeof value === "number" || typeof value === "boolean")
        return String(value)
      try {
        var text = JSON.stringify(value, null, 2)
        if (!text || text === "{}" || text === "[]")
          return "-"
        return text
      } catch (err) {
        try {
          return String(value)
        } catch (error) {
          return "-"
        }
      }
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
      normalizeArray(Datas.TaskDatas.controlCommands).forEach(function(entry) {
        if (entry === undefined || entry === null)
          return
        var row = {}
        row.id = readValue(entry, ['id', 'task_id', 'taskId'])
        row.sequence = row.id !== undefined && row.id !== null ? row.id : seq++
        var payload = entry.payload && typeof entry.payload === 'object' ? entry.payload : {}
        var commandKey = safeText(readValue(entry, ['command_key', 'commandKey', 'command']), '')
        if (!commandKey || commandKey === '-')
          commandKey = safeText(readValue(payload, ['action_key', 'action']), commandKey)
        row.commandKey = commandKey && commandKey.length ? commandKey : "-"
        var commandName = safeText(readValue(entry, ['command_name', 'commandName']), '')
        if (!commandName || commandName === '-')
          commandName = safeText(payload.action_name, '')
        row.commandName = commandName && commandName.length ? commandName : friendlyCommandName(row.commandKey)
        var paramsSource = entry.command_params !== undefined ? entry.command_params : payload.params
        row.paramsText = formatJson(paramsSource)
        var statusDetail = entry.status_detail !== undefined ? entry.status_detail : entry.statusDetail
        if (!statusDetail && entry.t_status_detail !== undefined)
          statusDetail = entry.t_status_detail
        row.detailText = formatJson(statusDetail)
        row.statusRaw = readValue(entry, ['status', 'state', 'result'])
        if (row.statusRaw === undefined && typeof statusDetail === "object")
          row.statusRaw = readValue(statusDetail, ['state', 'status'])
        if (row.statusRaw === undefined)
          row.statusText = qsTr('未执行')
        else
          row.statusText = taskStatusText(row.statusRaw)
        row.statusTone = statusColor(row.statusRaw !== undefined ? row.statusRaw : "PENDING")
        var timeCandidate = readValue(entry, ['updated_time', 'updatedTime', 'created_time', 'createdTime', 'timestamp'])
        if (!timeCandidate && typeof statusDetail === "object")
          timeCandidate = readValue(statusDetail, ['updated_at', 'finished_at', 'started_at'])
        if (!timeCandidate && payload.queued_at !== undefined)
          timeCandidate = payload.queued_at
        row.timeText = formatTimestamp(timeCandidate)
        var remark = readValue(entry, ['remark', 'note'])
        if (!remark && typeof payload === "object")
          remark = payload.remark || payload.note
        if (!remark && typeof statusDetail === "object")
          remark = statusDetail && (statusDetail.message || statusDetail.detail)
        row.remark = remark ? safeText(remark, "-") : "-"
        rows.push(row)
      })
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
      var health = statusSnapshot.task_runner_health || statusSnapshot.taskRunnerHealth || runnerHealth
      runnerHealth = (health && typeof health === "object") ? health : ({})
    }

    function processRunnerHealth(payload) {
      var source = payload ? (payload.task_runner_health || payload.taskRunnerHealth) : null
      var health = (source && typeof source === "object") ? source : ({})
      if (health.alert_key === undefined && health.alertKey !== undefined)
        health.alert_key = health.alertKey
      runnerHealth = health
      var key = ""
      if (health.alert_key !== undefined && health.alert_key !== null) {
        key = String(health.alert_key)
      }
      if (health.status === "error") {
        if (!key.length)
          key = "task_runner_offline"
        if (lastRunnerAlertKey !== key) {
          Cores.CoreError.showError(safeText(health.message, qsTr("任务执行程序离线")))
          lastRunnerAlertKey = key
        }
      } else if (health.status === "ok") {
        if (health.recovered && lastRunnerAlertKey)
          showAction(qsTr("任务执行程序已恢复"))
        lastRunnerAlertKey = ""
      }
    }
    Connections {
      target: Datas.StatusDatas
      function onMessageReceived(payload) {
        root.processRunnerHealth(payload)
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
