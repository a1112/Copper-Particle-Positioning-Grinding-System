import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

ApplicationWindow {
    id: window
    width: 1080
    height: 720
    visible: true
    title: qsTr("API 与 UI 测试窗口")

    // Signals bubble actions to the Python side for wiring into the real API.
    signal apiCallRequested(string endpoint, var options)
    signal uiActionRequested(string actionId, var options)
    signal refreshUiStateRequested()
    signal diagnosticsRequested(string category)

    property string baseUrl: "http://localhost:8000/api"
    property bool autoLogRequests: true

    readonly property var systemActions: [
        { label: qsTr("系统初始化"), endpoint: "system/init", method: "POST" },
        { label: qsTr("关闭系统"), endpoint: "system/shutdown", method: "POST" },
        { label: qsTr("获取状态摘要"), endpoint: "status/summary", method: "GET" },
        { label: qsTr("复位故障"), endpoint: "system/reset_faults", method: "POST" },
        { label: qsTr("重新加载配置"), endpoint: "config/reload", method: "POST" }
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

    ListModel {
        id: logModel
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
        if (!action || !action.endpoint)
            return

        var options = {
            method: action.method || "GET",
            baseUrl: baseUrl,
            payload: action.payload !== undefined ? action.payload : {}
        }

        if (action.query !== undefined)
            options.query = action.query

        apiCallRequested(action.endpoint, options)
    }

    function triggerUiAction(action) {
        if (!action || !action.actionId)
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
                        placeholderText: "status/ping"
                        text: "status/ping"
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

                            window.apiCallRequested(
                                manualEndpointField.text,
                                {
                                    method: manualMethodBox.currentText,
                                    baseUrl: window.baseUrl,
                                    payload: payload
                                }
                            )
                        }
                    }
                }

                TextArea {
                    id: manualPayloadField
                    Layout.fillWidth: true
                    Layout.preferredHeight: 100
                    placeholderText: "{\n    \"示例\": true\n}"
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
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

ApplicationWindow {
    id: window
    width: 1100
    height: 720
    visible: true
    title: qsTr("API 与 UI 测试窗口")

    property string baseUrl: "http://localhost:8000/api"
    property bool autoLogRequests: true

    property var systemActions: [
        { label: qsTr("状态 Ping"), endpoint: "status/ping", method: "GET" },
        { label: qsTr("状态摘要"), endpoint: "status/summary", method: "GET" },
        { label: qsTr("重新加载配置"), endpoint: "config/reload", method: "POST" },
        { label: qsTr("复位故障"), endpoint: "system/reset_faults", method: "POST" },
        { label: qsTr("进入维护模式"), endpoint: "system/maintenance", method: "POST", payload: { mode: "enter" } },
        { label: qsTr("退出维护模式"), endpoint: "system/maintenance", method: "POST", payload: { mode: "exit" } }
    ]

    property var processActions: [
        { label: qsTr("启动打磨流程"), endpoint: "process/start", method: "POST", payload: { recipe: "default" } },
        { label: qsTr("暂停流程"), endpoint: "process/pause", method: "POST" },
        { label: qsTr("恢复流程"), endpoint: "process/resume", method: "POST" },
        { label: qsTr("终止流程"), endpoint: "process/abort", method: "POST" },
        { label: qsTr("加载配方A"), endpoint: "process/recipe/load", method: "POST", payload: { name: "RecipeA" } },
        { label: qsTr("列出配方"), endpoint: "process/recipe/list", method: "GET" }
    ]

    property var deviceActions: [
        { label: qsTr("轴全部回零"), endpoint: "devices/motion/home_all", method: "POST" },
        { label: qsTr("X轴正向点动"), endpoint: "devices/motion/jog", method: "POST", payload: { axis: "X", distance: 1.0 } },
        { label: qsTr("X轴反向点动"), endpoint: "devices/motion/jog", method: "POST", payload: { axis: "X", distance: -1.0 } },
        { label: qsTr("使能伺服"), endpoint: "devices/motion/enable", method: "POST" },
        { label: qsTr("关闭伺服"), endpoint: "devices/motion/disable", method: "POST" },
        { label: qsTr("读取传感器"), endpoint: "devices/sensors/read_all", method: "GET" }
    ]

    property var visionActions: [
        { label: qsTr("捕获帧"), endpoint: "vision/capture", method: "POST" },
        { label: qsTr("运行对位"), endpoint: "vision/alignment/run", method: "POST" },
        { label: qsTr("校准相机"), endpoint: "vision/calibrate", method: "POST" },
        { label: qsTr("切换叠加层"), actionId: "vision/toggle_overlay" },
        { label: qsTr("显示最近检测"), endpoint: "vision/inspection/latest", method: "GET" },
        { label: qsTr("导出快照"), actionId: "vision/export_snapshot" }
    ]

    property var uiActions: [
        { label: qsTr("显示告警抽屉"), actionId: "ui/show_alarm_drawer" },
        { label: qsTr("隐藏告警抽屉"), actionId: "ui/hide_alarm_drawer" },
        { label: qsTr("打开工单对话框"), actionId: "ui/open_job_dialog" },
        { label: qsTr("关闭工单对话框"), actionId: "ui/close_job_dialog" },
        { label: qsTr("切换暗色模式"), actionId: "ui/toggle_dark_mode" },
        { label: qsTr("聚焦视觉面板"), actionId: "ui/focus_vision_panel" }
    ]

    property var diagnosticCategories: [
        { label: qsTr("系统快照"), category: "system" },
        { label: qsTr("工艺追踪"), category: "process" },
        { label: qsTr("设备遥测"), category: "device" },
        { label: qsTr("视觉指标"), category: "vision" },
        { label: qsTr("界面布局导出"), category: "ui" }
    ]

    signal apiCallRequested(string endpoint, var options)
    signal uiActionRequested(string actionId, var options)
    signal refreshUiStateRequested()
    signal diagnosticsRequested(string category)

    ListModel {
        id: logModel
    }

    function appendLog(message) {
        logModel.insert(0, {
                            timestamp: Qt.formatDateTime(new Date(), "hh:mm:ss"),
                            message: message
                        })
        if (logModel.count > 250) {
            logModel.remove(logModel.count - 1)
        }
    }

    onApiCallRequested: {
        if (window.autoLogRequests) {
            window.appendLog("API 调用 -> " + endpoint + " " + JSON.stringify(options))
        }
    }

    onUiActionRequested: {
        if (window.autoLogRequests) {
            window.appendLog("界面操作 -> " + actionId + " " + JSON.stringify(options))
        }
    }

    onRefreshUiStateRequested: {
        if (window.autoLogRequests) {
            window.appendLog("请求刷新界面")
        }
    }

    onDiagnosticsRequested: {
        if (window.autoLogRequests) {
            window.appendLog("诊断 -> " + category)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        GroupBox {
            title: qsTr("API 连接")
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
                        onEditingFinished: window.baseUrl = text
                    }

                    Button {
                        text: qsTr("应用")
                        onClicked: window.baseUrl = baseUrlField.text
                    }

                    Switch {
                        id: logSwitch
                        checked: window.autoLogRequests
                        text: qsTr("自动记录")
                        onToggled: window.autoLogRequests = checked
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Button {
                        text: qsTr("Ping 接口")
                        onClicked: window.apiCallRequested("status/ping", {
                            method: "GET",
                            baseUrl: window.baseUrl
                        })
                    }

                    Button {
                        text: qsTr("健康检查")
                        onClicked: window.apiCallRequested("status/health", {
                            method: "GET",
                            baseUrl: window.baseUrl
                        })
                    }

                    Button {
                        text: qsTr("重新加载配置")
                        onClicked: window.apiCallRequested("config/reload", {
                            method: "POST",
                            baseUrl: window.baseUrl
                        })
                    }

                    Button {
                        text: qsTr("列出任务")
                        onClicked: window.apiCallRequested("jobs/active", {
                            method: "GET",
                            baseUrl: window.baseUrl
                        })
                    }

                    Item {
                        Layout.fillWidth: true
                    }

                    Button {
                        text: qsTr("刷新界面状态")
                        onClicked: window.refreshUiStateRequested()
                    }
                }
            }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            ColumnLayout {
                id: actionColumn
                width: parent.width
                spacing: 12

                GroupBox {
                    title: qsTr("系统控制")
                    Layout.fillWidth: true

                    Flow {
                        width: parent.width
                        spacing: 8
                        Repeater {
                            model: window.systemActions
                            delegate: Button {
                                text: modelData.label
                                width: Math.max(200, implicitWidth)
                                onClicked: window.apiCallRequested(modelData.endpoint, {
                                    method: modelData.method,
                                    baseUrl: window.baseUrl,
                                    payload: modelData.payload !== undefined ? modelData.payload : ({})
                                })
                            }
                        }
                    }
                }

                GroupBox {
                    title: qsTr("工艺控制")
                    Layout.fillWidth: true

                    Flow {
                        width: parent.width
                        spacing: 8
                        Repeater {
                            model: window.processActions
                            delegate: Button {
                                text: modelData.label
                                width: Math.max(200, implicitWidth)
                                onClicked: window.apiCallRequested(modelData.endpoint, {
                                    method: modelData.method,
                                    baseUrl: window.baseUrl,
                                    payload: modelData.payload !== undefined ? modelData.payload : ({})
                                })
                            }
                        }
                    }
                }

                GroupBox {
                    title: qsTr("设备控制")
                    Layout.fillWidth: true

                    Flow {
                        width: parent.width
                        spacing: 8
                        Repeater {
                            model: window.deviceActions
                            delegate: Button {
                                text: modelData.label
                                width: Math.max(200, implicitWidth)
                                onClicked: window.apiCallRequested(modelData.endpoint, {
                                    method: modelData.method,
                                    baseUrl: window.baseUrl,
                                    payload: modelData.payload !== undefined ? modelData.payload : ({})
                                })
                            }
                        }
                    }
                }

                GroupBox {
                    title: qsTr("视觉控制")
                    Layout.fillWidth: true

                    Flow {
                        width: parent.width
                        spacing: 8
                        Repeater {
                            model: window.visionActions
                            delegate: Button {
                                text: modelData.label
                                width: Math.max(200, implicitWidth)
                                onClicked: {
                                    if (modelData.endpoint !== undefined) {
                                        window.apiCallRequested(modelData.endpoint, {
                                            method: modelData.method,
                                            baseUrl: window.baseUrl,
                                            payload: modelData.payload !== undefined ? modelData.payload : ({})
                                        })
                                    } else if (modelData.actionId !== undefined) {
                                        window.uiActionRequested(modelData.actionId, {})
                                    }
                                }
                            }
                        }
                    }
                }

                GroupBox {
                    title: qsTr("界面操作")
                    Layout.fillWidth: true

                    Flow {
                        width: parent.width
                        spacing: 8
                        Repeater {
                            model: window.uiActions
                            delegate: Button {
                                text: modelData.label
                                width: Math.max(200, implicitWidth)
                                onClicked: window.uiActionRequested(modelData.actionId, modelData.options !== undefined ? modelData.options : ({}))
                            }
                        }
                    }
                }

                GroupBox {
                    title: qsTr("诊断快照")
                    Layout.fillWidth: true

                    Flow {
                        width: parent.width
                        spacing: 8
                        Repeater {
                            model: window.diagnosticCategories
                            delegate: Button {
                                text: modelData.label
                                width: Math.max(200, implicitWidth)
                                onClicked: window.diagnosticsRequested(modelData.category)
                            }
                        }
                    }
                }

                GroupBox {
                    title: qsTr("自定义 API 请求")
                    Layout.fillWidth: true

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            ComboBox {
                                id: methodCombo
                                model: ["GET", "POST", "PUT", "DELETE", "PATCH"]
                                Layout.preferredWidth: 110
                            }

                            TextField {
                                id: endpointField
                                Layout.fillWidth: true
                                placeholderText: "/自定义/接口"
                            }

                            Button {
                                text: qsTr("发送")
                                onClicked: {
                                    var body = {}
                                    var raw = payloadArea.text.trim()
                                    if (raw.length > 0) {
                                        try {
                                            body = JSON.parse(raw)
                                        } catch (error) {
                                            window.appendLog("JSON 负载无效: " + error)
                                            return
                                        }
                                    }
                                    window.apiCallRequested(endpointField.text, {
                                        method: methodCombo.currentText,
                                        baseUrl: window.baseUrl,
                                        payload: body
                                    })
                                }
                            }
                        }

                        TextArea {
                            id: payloadArea
                            Layout.fillWidth: true
                            Layout.preferredHeight: 140
                            wrapMode: TextEdit.NoWrap
                            placeholderText: qsTr("{\n    \"key\": \"value\"\n}")
                            font.family: "Consolas"
                            font.pointSize: 10
                        }
                    }
                }
            }
        }

        Frame {
            Layout.fillWidth: true
            Layout.preferredHeight: 220

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true

                    Label {
                        text: qsTr("活动日志")
                        font.bold: true
                    }

                    Item {
                        Layout.fillWidth: true
                    }

                    Button {
                        text: qsTr("复制最新")
                        onClicked: {
                            if (logModel.count > 0) {
                                Qt.application.clipboard.text = logModel.get(0).message
                                window.appendLog("已复制最新记录到剪贴板")
                            }
                        }
                    }

                    Button {
                        text: qsTr("清空日志")
                        onClicked: logModel.clear()
                    }
                }

                ListView {
                    id: logView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    model: logModel
                    delegate: Rectangle {
                        width: logView.width
                        height: implicitHeight
                        color: index % 2 === 0 ? "#23242a" : "#1c1d21"

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 8

                            Label {
                                text: model.timestamp
                                font.family: "Consolas"
                                font.pointSize: 10
                                color: "#cbd5f5"
                            }

                            Label {
                                Layout.fillWidth: true
                                text: model.message
                                color: "#f5f7ff"
                                wrapMode: Text.WordWrap
                            }
                        }
                    }

                    ScrollBar.vertical: ScrollBar { }
                }
            }
        }
    }
}


