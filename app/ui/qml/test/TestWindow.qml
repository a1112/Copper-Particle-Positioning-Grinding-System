import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import "../Api" as Api

ApplicationWindow {
    id: window
    width: 1080
    height: 720
    visible: false
    title: qsTr("API 与 UI 测试窗口")

    // Signals bubble actions to the Python side for wiring into the real API.
    signal apiCallRequested(string endpoint, var options)
    signal uiActionRequested(string actionId, var options)
    signal refreshUiStateRequested()
    signal diagnosticsRequested(string category)

    property string baseUrl: "http://localhost:8000/api"
    property bool autoLogRequests: true

    Component.onCompleted: {
        try {
            if (Api && Api.Urls && Api.Urls.base) {
                window.baseUrl = Api.Urls.base()
            }
        } catch (err) {
            // ignore
        }
        if (typeof baseUrlField !== "undefined" && baseUrlField) {
            baseUrlField.text = window.baseUrl
        }
    }

    readonly property var systemActions: [
        { label: qsTr("系统初始化"), endpoint: "system/init", method: "POST" },
        { label: qsTr("关闭系统"), endpoint: "system/shutdown", method: "POST" },
        { label: qsTr("获取状态摘要"), endpoint: "status/summary", method: "GET" },
        { label: qsTr("复位故障"), endpoint: "system/reset_faults", method: "POST" },
        { label: qsTr("重新加载配置"), endpoint: "config/reload", method: "POST" },
        {
            label: qsTr("报警测试"),
            endpoint: "diagnostics/alarms/test",
            method: "POST",
            payload: function() {
                return {
                    message: "UI测试报警 " + Qt.formatDateTime(new Date(), "hh:mm:ss"),
                    level: 3
                }
            },
            onSuccess: function(resp) {
                var alarm = resp && resp.alarm ? resp.alarm : null
                if (alarm) {
                    window.appendLog(qsTr("报警写入成功: %1 %2").arg(alarm.code || "-").arg(alarm.message || "-"))
                } else {
                    window.appendLog(qsTr("报警写入成功: %1").arg(JSON.stringify(resp || {})))
                }
            },
            onError: function(status, message) {
                window.appendLog(qsTr("报警写入失败(%1): %2").arg(status).arg(message))
            }
        }
    ]

    readonly property var processActions: [
        { label: qsTr("启动打磨流程"), endpoint: "process/start", method: "POST", payload: { recipe: "default" } },
        { label: qsTr("暂停流程"), endpoint: "process/pause", method: "POST" },
        { label: qsTr("恢复流程"), endpoint: "process/resume", method: "POST" },
        { label: qsTr("终止流程"), endpoint: "process/abort", method: "POST" },
        { label: qsTr("前进一步"), endpoint: "process/advance_step", method: "POST" }
    ]

    readonly property var deviceActions: [
        { label: qsTr("龙门回零"), endpoint: "devices/gantry/home", method: "POST" },
        { label: qsTr("校准主轴"), endpoint: "devices/spindle/calibrate", method: "POST" },
        { label: qsTr("测量称重传感器"), endpoint: "devices/load_cell/sample", method: "GET" },
        { label: qsTr("切换真空"), endpoint: "devices/vacuum/toggle", method: "POST" },
        { label: qsTr("模拟故障"), endpoint: "devices/simulator/fault", method: "POST", payload: { code: "TEST_FAULT" } }
    ]

    readonly property var visionActions: [
        { label: qsTr("采集图像"), endpoint: "vision/capture", method: "POST" },
        { label: qsTr("运行对位"), endpoint: "vision/alignment", method: "POST" },
        { label: qsTr("检测工件"), endpoint: "vision/inspection", method: "POST", payload: { mode: "quick" } },
        { label: qsTr("校准相机"), endpoint: "vision/calibration", method: "POST" },
        { label: qsTr("获取叠加层"), endpoint: "vision/overlays", method: "GET" }
    ]

    readonly property var uiActions: [
        { label: qsTr("聚焦相机视图"), actionId: "ui/focus_camera", options: { view: "main" } },
        { label: qsTr("切换叠加层"), actionId: "ui/toggle_overlay", options: { overlay: "particle_map" } },
        { label: qsTr("显示告警对话框"), actionId: "ui/show_alert", options: { level: "warning", message: "来自测试工具的告警" } },
        { label: qsTr("打开配方编辑器"), actionId: "ui/open_recipe_editor", options: {} },
        { label: qsTr("刷新仪表盘"), actionId: "ui/reload_dashboard", options: {} }
    ]

    readonly property var statusScenarios: [
        ({
            label: qsTr("空闲 · 待命准备"),
            status: {
                state: "IDLE",
                run_mode: "SIM",
                serial_number: "SIM-0001",
                tool_usage: "0%",
                cutter_diameter: "80mm",
                tool_life: "0 h",
                particle_count: 0,
                plane_height: "-0.20",
                position: { "x": 0.0, "y": 0.0, "z": 50.0, "theta": 0.0 },
                spindle_rpm: 0,
                spindle_torque: 0.05,
                feed_rate: 0.0,
                travel_speed: 0.0,
                seriesA: 0,
                seriesB: 0.05,
                statusLights: { camera: "READY", spindle: "READY", device: "IDLE", interlock: true, server: true },
                lights: { camera: "READY", spindle: "READY", device: "IDLE", interlock: true, server: true }
            },
            cutting: {
                feed_rate: 0.0,
                downfeed_target: 0.8,
                downfeed_current: 0.0,
                removal_current: 0.0,
                removal_expected: 120.0,
                torque_max: 0.1,
                torque: 0.05,
                elapsed_sec: 0
            }
        }),
        ({
            label: qsTr("加工 · 正常切削"),
            status: {
                state: "RUNNING",
                run_mode: "AUTO",
                serial_number: "SIM-0002",
                tool_usage: "36%",
                cutter_diameter: "80mm",
                tool_life: "1.8 h",
                particle_count: 320,
                plane_height: "-0.32",
                position: { "x": 125.4, "y": 42.8, "z": -0.46, "theta": 0.75 },
                spindle_rpm: 2350,
                spindle_torque: 0.58,
                feed_rate: 24.0,
                travel_speed: 52.0,
                seriesA: 2350,
                seriesB: 0.58,
                statusLights: { camera: "READY", spindle: "RUNNING", device: "RUNNING", interlock: true, server: true },
                lights: { camera: "READY", spindle: "RUNNING", device: "RUNNING", interlock: true, server: true }
            },
            cutting: {
                feed_rate: 24.0,
                downfeed_target: 0.8,
                downfeed_current: 0.58,
                removal_current: 48.3,
                removal_expected: 120.0,
                torque_max: 0.62,
                torque: 0.55,
                elapsed_sec: 360
            }
        }),
        ({
            label: qsTr("报警 · 主轴过载"),
            status: {
                state: "FAULT",
                run_mode: "AUTO",
                serial_number: "SIM-0003",
                tool_usage: "88%",
                cutter_diameter: "80mm",
                tool_life: "4.6 h",
                particle_count: 512,
                plane_height: "-0.45",
                fault_code: "SPINDLE_OVERLOAD",
                fault_message: qsTr("主轴扭矩达到限制"),
                position: { "x": 182.0, "y": 58.5, "z": -1.25, "theta": 1.2 },
                spindle_rpm: 80,
                spindle_torque: 1.25,
                feed_rate: 0.0,
                travel_speed: 0.0,
                seriesA: 80,
                seriesB: 1.25,
                statusLights: { camera: "WARNING", spindle: "FAULT", device: "FAULT", interlock: false, server: true },
                lights: { camera: "WARNING", spindle: "FAULT", device: "FAULT", interlock: false, server: true },
                alerts: [
                    { level: "error", message: qsTr("主轴扭矩异常，请检查负载") }
                ]
            },
            cutting: {
                feed_rate: 0.0,
                downfeed_target: 0.8,
                downfeed_current: 0.8,
                removal_current: 97.5,
                removal_expected: 120.0,
                torque_max: 1.3,
                torque: 1.25,
                elapsed_sec: 520
            }
        })
    ]

    ListModel {
        id: logModel
    }

    function resolveRequestUrl(endpoint) {
        var target = ""
        if (endpoint !== undefined && endpoint !== null) {
            target = String(endpoint).trim()
        }
        if (target.length > 0 && target.indexOf("://") >= 0)
            return target
        var base = window.baseUrl ? String(window.baseUrl).trim() : ""
        if (base.length === 0)
            base = "http://localhost:8000/api"
        if (base.endsWith("/"))
            base = base.slice(0, base.length - 1)
        if (target.length === 0)
            return base
        if (target.startsWith("/"))
            target = target.slice(1)
        return base + "/" + target
    }

    function performApiRequest(endpoint, method, payload, onSuccess, onError) {
        var verb = method !== undefined ? method : "GET"
        verb = String(verb).toUpperCase()
        var url = resolveRequestUrl(endpoint)
        var bodyAllowed = ["GET", "HEAD"].indexOf(verb) === -1
        var bodyValue = bodyAllowed ? (payload !== undefined && payload !== null ? payload : {}) : null

        apiCallRequested(endpoint !== undefined && endpoint !== null ? endpoint : "", {
            method: verb,
            baseUrl: window.baseUrl,
            payload: bodyValue
        })

        var xhr = new XMLHttpRequest()
        try {
            xhr.open(verb, url)
        } catch (openErr) {
            window.appendLog("API open error " + verb + " " + url + " : " + openErr)
            if (onError) onError(-1, String(openErr))
            return
        }
        if (bodyAllowed)
            xhr.setRequestHeader("Content-Type", "application/json")
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE)
                return
            var status = xhr.status
            var text = xhr.responseText !== undefined && xhr.responseText !== null ? xhr.responseText : ""
            if (status >= 200 && status < 300) {
                var result = {}
                if (text.length > 0) {
                    try { result = JSON.parse(text) } catch (parseErr) { result = {} }
                }
                if (onSuccess)
                    onSuccess(result, status)
                else
                    window.appendLog("API success " + verb + " " + url + " <- " + text)
            } else {
                if (onError)
                    onError(status, text)
                else
                    window.appendLog("API failure " + verb + " " + url + " -> " + status + " " + text)
            }
        }
        xhr.onerror = function() {
            var msg = "API network error " + verb + " " + url
            window.appendLog(msg)
            if (onError)
                onError(-1, msg)
        }
        try {
            if (bodyAllowed)
                xhr.send(JSON.stringify(bodyValue))
            else
                xhr.send()
        } catch (sendErr) {
            var detail = "API send error " + verb + " " + url + " : " + sendErr
            window.appendLog(detail)
            if (onError)
                onError(-1, String(sendErr))
        }
    }

    function clonePayload(payload) {
        if (payload === undefined)
            return null
        if (payload === null)
            return null
        try {
            return JSON.parse(JSON.stringify(payload))
        } catch (err) {
            return payload
        }
    }

    function sendScenario(scenario) {
        if (!scenario)
            return
        var statusPayload = clonePayload(scenario.status)
        var cuttingPayload = clonePayload(scenario.cutting)
        var nowTs = Math.round(Date.now() / 1000)

        if (statusPayload) {
            statusPayload.timestamp = new Date().toISOString()
            if (statusPayload.seriesA === undefined && statusPayload.spindle_rpm !== undefined)
                statusPayload.seriesA = statusPayload.spindle_rpm
            if (statusPayload.seriesB === undefined && statusPayload.spindle_torque !== undefined)
                statusPayload.seriesB = statusPayload.spindle_torque
            performApiRequest("status/test_payload", "POST", statusPayload,
                function() {
                    window.appendLog(qsTr("状态测试数据已提交: %1").arg(scenario.label))
                },
                function(code, message) {
                    window.appendLog(qsTr("状态测试数据失败(%1): %2").arg(code).arg(message))
                })
        }
        if (cuttingPayload) {
            if (cuttingPayload.ts === undefined)
                cuttingPayload.ts = nowTs
            performApiRequest("cutting/test_payload", "POST", cuttingPayload,
                function() {
                    window.appendLog(qsTr("切削测试数据已提交: %1").arg(scenario.label))
                },
                function(code, message) {
                    window.appendLog(qsTr("切削测试数据失败(%1): %2").arg(code).arg(message))
                })
        }
    }

    function resetTestPayloads() {
        performApiRequest("status/test_payload", "DELETE", null,
            function() {
                window.appendLog(qsTr("已恢复状态模拟值"))
            },
            function(code, message) {
                window.appendLog(qsTr("恢复状态数据失败(%1): %2").arg(code).arg(message))
            })
        performApiRequest("cutting/test_payload", "DELETE", null,
            function() {
                window.appendLog(qsTr("已恢复切削模拟值"))
            },
            function(code, message) {
                window.appendLog(qsTr("恢复切削数据失败(%1): %2").arg(code).arg(message))
            })
    }

    function fetchManualSnapshots() {
        performApiRequest("status/test_payload", "GET", null,
            function(resp) {
                window.appendLog(qsTr("状态覆盖: %1").arg(JSON.stringify(resp)))
            },
            function(code, message) {
                window.appendLog(qsTr("读取状态覆盖失败(%1): %2").arg(code).arg(message))
            })
        performApiRequest("cutting/test_payload", "GET", null,
            function(resp) {
                window.appendLog(qsTr("切削覆盖: %1").arg(JSON.stringify(resp)))
            },
            function(code, message) {
                window.appendLog(qsTr("读取切削覆盖失败(%1): %2").arg(code).arg(message))
            })
    }

    function appendLog(message) {
        logModel.insert(0, {
            "timestamp": Qt.formatDateTime(new Date(), "hh:mm:ss"),
            "message": message
        })
    }

    function clearLog() {
        logModel.clear()
    }

    function triggerApiAction(action) {
        if (!action)
            return
        if (!action.endpoint)
            return

        var endpoint = action.endpoint
        if (action.query !== undefined && action.query !== null) {
            if (typeof action.query === "string") {
                var qs = action.query
                endpoint = endpoint + (qs.startsWith("?") ? qs : ("?" + qs))
            } else if (typeof action.query === "object") {
                var parts = []
                for (var key in action.query) {
                    if (!action.query.hasOwnProperty(key))
                        continue
                    var value = action.query[key]
                    parts.push(encodeURIComponent(key) + "=" + encodeURIComponent(value))
                }
                if (parts.length > 0)
                    endpoint = endpoint + "?" + parts.join("&")
            }
        }

        var payload = {}
        if (action.payload !== undefined) {
            if (typeof action.payload === "function") {
                try {
                    payload = action.payload()
                } catch (payloadErr) {
                    window.appendLog(qsTr("生成请求体失败: %1").arg(payloadErr))
                    payload = {}
                }
            } else {
                payload = action.payload
            }
        }
        var method = action.method !== undefined ? action.method : "GET"
        var successHandler = action.onSuccess !== undefined ? action.onSuccess : null
        var errorHandler = action.onError !== undefined ? action.onError : null
        performApiRequest(endpoint, method, payload, successHandler, errorHandler)
    }

    function triggerUiAction(action) {
        if (!action)
            return
        if (!action.actionId)
            return

        var options = action.options !== undefined ? action.options : {}
        uiActionRequested(action.actionId, options)
    }

    onApiCallRequested: {
        if (autoLogRequests) {
            appendLog("API 调用 " + endpoint + " -> " + JSON.stringify(options))
        }
    }

    onUiActionRequested: {
        if (autoLogRequests) {
            appendLog("界面操作 " + actionId + " -> " + JSON.stringify(options))
        }
    }

    onRefreshUiStateRequested: appendLog("请求刷新界面")
    onDiagnosticsRequested: appendLog("请求诊断: " + category)

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        GroupBox {
            title: qsTr("会话控制")
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Label {
                        text: qsTr("基础 URL")
                        Layout.alignment: Qt.AlignVCenter
                    }

                    TextField {
                        id: baseUrlField
                        Layout.fillWidth: true
                        text: window.baseUrl
                        placeholderText: "http://localhost:8000/api"
                        selectByMouse: true
                        onEditingFinished: window.baseUrl = text.length > 0 ? text : window.baseUrl
                    }

                    Button {
                        text: qsTr("应用")
                        onClicked: window.baseUrl = baseUrlField.text.length > 0 ? baseUrlField.text : window.baseUrl
                    }

                    Button {
                        text: qsTr("Ping 接口")
                        onClicked: window.triggerApiAction({ endpoint: "status/ping", method: "GET" })
                    }

                    Button {
                        text: qsTr("刷新界面状态")
                        onClicked: {
                            window.refreshUiStateRequested()
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Switch {
                        id: autoLogSwitch
                        text: qsTr("自动记录请求")
                        checked: window.autoLogRequests
                        Layout.alignment: Qt.AlignVCenter
                        onToggled: window.autoLogRequests = checked
                    }

                    Button {
                        text: qsTr("执行诊断")
                        onClicked: window.diagnosticsRequested("full")
                    }
                }
            }
        }

        GroupBox {
            title: qsTr("手动 API 请求")
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Label {
                        text: qsTr("接口路径")
                        Layout.alignment: Qt.AlignVCenter
                    }

                    TextField {
                        id: manualEndpointField
                        Layout.fillWidth: true
                        placeholderText: "status/test_payload"
                        text: "status/test_payload"
                        selectByMouse: true
                    }

                    ComboBox {
                        id: manualMethodBox
                        Layout.preferredWidth: 100
                        model: ["GET", "POST", "PUT", "DELETE"]
                    }

                    Button {
                        text: qsTr("发送")
                        onClicked: {
                            if (manualEndpointField.text.length === 0) {
                                window.appendLog("手动请求缺少接口路径")
                                return
                            }

                            var payload = {}
                            if (manualPayloadField.text.length > 0) {
                                try {
                                    payload = JSON.parse(manualPayloadField.text)
                                } catch (err) {
                                    window.appendLog("负载解析出错: " + err)
                                    return
                                }
                            }

                            performApiRequest(
                                manualEndpointField.text,
                                manualMethodBox.currentText,
                                payload,
                                function(resp) {
                                    window.appendLog(qsTr("手动请求响应: %1").arg(JSON.stringify(resp)))
                                },
                                function(status, message) {
                                    window.appendLog(qsTr("手动请求失败(%1): %2").arg(status).arg(message))
                                }
                            )
                        }
                    }
                }

                TextArea {
                    id: manualPayloadField
                    Layout.fillWidth: true
                    Layout.preferredHeight: 100
                    placeholderText: "{\n    \"state\": \"RUNNING\",\n    \"spindle_rpm\": 2200\n}"
                    wrapMode: TextEdit.NoWrap
                }
            }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true

            Column {
                width: parent.width
                spacing: 16

                GroupBox {
                    title: qsTr("测试数据注入")
                    Layout.fillWidth: true

                    Column {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        Flow {
                            width: parent.width
                            spacing: 8

                            Repeater {
                                model: window.statusScenarios
                                delegate: Button {
                                    text: modelData.label
                                    onClicked: window.sendScenario(modelData)
                                }
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Button {
                                text: qsTr("恢复模拟输出")
                                onClicked: window.resetTestPayloads()
                            }

                            Button {
                                text: qsTr("查看当前覆盖")
                                onClicked: window.fetchManualSnapshots()
                            }

                            Item { Layout.fillWidth: true }
                        }
                    }
                }

                GroupBox {
                    title: qsTr("系统 API")
                    Layout.fillWidth: true

                    Column {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        Flow {
                            width: parent.width
                            spacing: 8

                            Repeater {
                                model: window.systemActions
                                delegate: Button {
                                    text: modelData.label
                                    onClicked: window.triggerApiAction(modelData)
                                }
                            }
                        }
                    }
                }

                GroupBox {
                    title: qsTr("工艺 API")
                    Layout.fillWidth: true

                    Column {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        Flow {
                            width: parent.width
                            spacing: 8

                            Repeater {
                                model: window.processActions
                                delegate: Button {
                                    text: modelData.label
                                    onClicked: window.triggerApiAction(modelData)
                                }
                            }
                        }
                    }
                }

                GroupBox {
                    title: qsTr("设备 API")
                    Layout.fillWidth: true

                    Column {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        Flow {
                            width: parent.width
                            spacing: 8

                            Repeater {
                                model: window.deviceActions
                                delegate: Button {
                                    text: modelData.label
                                    onClicked: window.triggerApiAction(modelData)
                                }
                            }
                        }
                    }
                }

                GroupBox {
                    title: qsTr("视觉 API")
                    Layout.fillWidth: true

                    Column {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        Flow {
                            width: parent.width
                            spacing: 8

                            Repeater {
                                model: window.visionActions
                                delegate: Button {
                                    text: modelData.label
                                    onClicked: window.triggerApiAction(modelData)
                                }
                            }
                        }
                    }
                }

                GroupBox {
                    title: qsTr("界面操作")
                    Layout.fillWidth: true

                    Column {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        Flow {
                            width: parent.width
                            spacing: 8

                            Repeater {
                                model: window.uiActions
                                delegate: Button {
                                    text: modelData.label
                                    onClicked: window.triggerUiAction(modelData)
                                }
                            }
                        }
                    }
                }
            }
        }

        GroupBox {
            title: qsTr("事件日志")
            Layout.fillWidth: true
            Layout.preferredHeight: 220

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8

                ListView {
                    id: logView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    model: logModel
                    delegate: RowLayout {
                        width: logView.width
                        spacing: 12

                        Label {
                            text: model.timestamp
                            font.family: "Monospace"
                            Layout.preferredWidth: 80
                        }

                        Text {
                            text: model.message
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                    }

                    ScrollBar.vertical: ScrollBar { }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Button {
                        text: qsTr("添加备注")
                        onClicked: window.appendLog("手动备注 " + Qt.formatDateTime(new Date(), "hh:mm:ss"))
                    }

                    Item { Layout.fillWidth: true }

                    Button {
                        text: qsTr("清空日志")
                        onClicked: window.clearLog()
                    }
                }
            }
        }
    }
}



