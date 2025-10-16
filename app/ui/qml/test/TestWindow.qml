import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

ApplicationWindow {
    id: window
    width: 1080
    height: 720
    visible: true
    title: qsTr("API & UI Test Window")

    // Signals bubble actions to the Python side for wiring into the real API.
    signal apiCallRequested(string endpoint, var options)
    signal uiActionRequested(string actionId, var options)
    signal refreshUiStateRequested()
    signal diagnosticsRequested(string category)

    property string baseUrl: "http://localhost:8000/api"
    property bool autoLogRequests: true

    readonly property var systemActions: [
        { label: qsTr("Initialize System"), endpoint: "system/init", method: "POST" },
        { label: qsTr("Shutdown System"), endpoint: "system/shutdown", method: "POST" },
        { label: qsTr("Get Status Summary"), endpoint: "status/summary", method: "GET" },
        { label: qsTr("Reset Faults"), endpoint: "system/reset_faults", method: "POST" },
        { label: qsTr("Reload Config"), endpoint: "config/reload", method: "POST" }
    ]

    readonly property var processActions: [
        { label: qsTr("Start Grind Cycle"), endpoint: "process/start", method: "POST", payload: { recipe: "default" } },
        { label: qsTr("Pause Cycle"), endpoint: "process/pause", method: "POST" },
        { label: qsTr("Resume Cycle"), endpoint: "process/resume", method: "POST" },
        { label: qsTr("Abort Cycle"), endpoint: "process/abort", method: "POST" },
        { label: qsTr("Advance Step"), endpoint: "process/advance_step", method: "POST" }
    ]

    readonly property var deviceActions: [
        { label: qsTr("Home Gantry"), endpoint: "devices/gantry/home", method: "POST" },
        { label: qsTr("Calibrate Spindle"), endpoint: "devices/spindle/calibrate", method: "POST" },
        { label: qsTr("Measure Load Cell"), endpoint: "devices/load_cell/sample", method: "GET" },
        { label: qsTr("Toggle Vacuum"), endpoint: "devices/vacuum/toggle", method: "POST" },
        { label: qsTr("Simulate Fault"), endpoint: "devices/simulator/fault", method: "POST", payload: { code: "TEST_FAULT" } }
    ]

    readonly property var visionActions: [
        { label: qsTr("Capture Image"), endpoint: "vision/capture", method: "POST" },
        { label: qsTr("Run Alignment"), endpoint: "vision/alignment", method: "POST" },
        { label: qsTr("Inspect Part"), endpoint: "vision/inspection", method: "POST", payload: { mode: "quick" } },
        { label: qsTr("Calibrate Camera"), endpoint: "vision/calibration", method: "POST" },
        { label: qsTr("Fetch Overlays"), endpoint: "vision/overlays", method: "GET" }
    ]

    readonly property var uiActions: [
        { label: qsTr("Focus Camera View"), actionId: "ui/focus_camera", options: { view: "main" } },
        { label: qsTr("Toggle Overlay"), actionId: "ui/toggle_overlay", options: { overlay: "particle_map" } },
        { label: qsTr("Show Alert Dialog"), actionId: "ui/show_alert", options: { level: "warning", message: "Test alert from harness" } },
        { label: qsTr("Open Recipe Editor"), actionId: "ui/open_recipe_editor", options: {} },
        { label: qsTr("Reload Dashboard"), actionId: "ui/reload_dashboard", options: {} }
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
            appendLog("API " + endpoint + " -> " + JSON.stringify(options))
        }
    }

    onUiActionRequested: {
        if (autoLogRequests) {
            appendLog("UI " + actionId + " -> " + JSON.stringify(options))
        }
    }

    onRefreshUiStateRequested: appendLog("UI refresh requested")
    onDiagnosticsRequested: appendLog("Diagnostics requested: " + category)

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        GroupBox {
            title: qsTr("Session Controls")
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Label {
                        text: qsTr("Base URL")
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
                        text: qsTr("Apply")
                        onClicked: window.baseUrl = baseUrlField.text.length > 0 ? baseUrlField.text : window.baseUrl
                    }

                    Button {
                        text: qsTr("Ping API")
                        onClicked: window.triggerApiAction({ endpoint: "status/ping", method: "GET" })
                    }

                    Button {
                        text: qsTr("Refresh UI State")
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
                        text: qsTr("Auto log requests")
                        checked: window.autoLogRequests
                        Layout.alignment: Qt.AlignVCenter
                        onToggled: window.autoLogRequests = checked
                    }

                    Button {
                        text: qsTr("Run Diagnostics")
                        onClicked: window.diagnosticsRequested("full")
                    }
                }
            }
        }

        GroupBox {
            title: qsTr("Manual API Request")
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Label {
                        text: qsTr("Endpoint")
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
                        text: qsTr("Send")
                        onClicked: {
                            if (manualEndpointField.text.length === 0) {
                                window.appendLog("Manual request missing endpoint")
                                return
                            }

                            var payload = {}
                            if (manualPayloadField.text.length > 0) {
                                try {
                                    payload = JSON.parse(manualPayloadField.text)
                                } catch (err) {
                                    window.appendLog("Payload parse error: " + err)
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
                    placeholderText: "{\n    \"example\": true\n}"
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
                    title: qsTr("System APIs")
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
                    title: qsTr("Process APIs")
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
                    title: qsTr("Device APIs")
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
                    title: qsTr("Vision APIs")
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
                    title: qsTr("UI Actions")
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
            title: qsTr("Event Log")
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
                        text: qsTr("Add Note")
                        onClicked: window.appendLog("Manual note at " + Qt.formatDateTime(new Date(), "hh:mm:ss"))
                    }

                    Item { Layout.fillWidth: true }

                    Button {
                        text: qsTr("Clear Log")
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
    title: qsTr("API & UI Test Window")

    property string baseUrl: "http://localhost:8000/api"
    property bool autoLogRequests: true

    property var systemActions: [
        { label: qsTr("Ping Status"), endpoint: "status/ping", method: "GET" },
        { label: qsTr("Summary Status"), endpoint: "status/summary", method: "GET" },
        { label: qsTr("Reload Config"), endpoint: "config/reload", method: "POST" },
        { label: qsTr("Reset Faults"), endpoint: "system/reset_faults", method: "POST" },
        { label: qsTr("Enter Maintenance"), endpoint: "system/maintenance", method: "POST", payload: { mode: "enter" } },
        { label: qsTr("Exit Maintenance"), endpoint: "system/maintenance", method: "POST", payload: { mode: "exit" } }
    ]

    property var processActions: [
        { label: qsTr("Start Grind Cycle"), endpoint: "process/start", method: "POST", payload: { recipe: "default" } },
        { label: qsTr("Pause Cycle"), endpoint: "process/pause", method: "POST" },
        { label: qsTr("Resume Cycle"), endpoint: "process/resume", method: "POST" },
        { label: qsTr("Abort Cycle"), endpoint: "process/abort", method: "POST" },
        { label: qsTr("Load Recipe A"), endpoint: "process/recipe/load", method: "POST", payload: { name: "RecipeA" } },
        { label: qsTr("List Recipes"), endpoint: "process/recipe/list", method: "GET" }
    ]

    property var deviceActions: [
        { label: qsTr("Home All Axes"), endpoint: "devices/motion/home_all", method: "POST" },
        { label: qsTr("Jog X+"), endpoint: "devices/motion/jog", method: "POST", payload: { axis: "X", distance: 1.0 } },
        { label: qsTr("Jog X-"), endpoint: "devices/motion/jog", method: "POST", payload: { axis: "X", distance: -1.0 } },
        { label: qsTr("Enable Motors"), endpoint: "devices/motion/enable", method: "POST" },
        { label: qsTr("Disable Motors"), endpoint: "devices/motion/disable", method: "POST" },
        { label: qsTr("Read Sensors"), endpoint: "devices/sensors/read_all", method: "GET" }
    ]

    property var visionActions: [
        { label: qsTr("Capture Frame"), endpoint: "vision/capture", method: "POST" },
        { label: qsTr("Run Alignment"), endpoint: "vision/alignment/run", method: "POST" },
        { label: qsTr("Calibrate Camera"), endpoint: "vision/calibrate", method: "POST" },
        { label: qsTr("Toggle Overlay"), actionId: "vision/toggle_overlay" },
        { label: qsTr("Show Last Inspection"), endpoint: "vision/inspection/latest", method: "GET" },
        { label: qsTr("Export Snapshot"), actionId: "vision/export_snapshot" }
    ]

    property var uiActions: [
        { label: qsTr("Show Alarm Drawer"), actionId: "ui/show_alarm_drawer" },
        { label: qsTr("Hide Alarm Drawer"), actionId: "ui/hide_alarm_drawer" },
        { label: qsTr("Open Job Dialog"), actionId: "ui/open_job_dialog" },
        { label: qsTr("Close Job Dialog"), actionId: "ui/close_job_dialog" },
        { label: qsTr("Toggle Dark Mode"), actionId: "ui/toggle_dark_mode" },
        { label: qsTr("Focus Vision Panel"), actionId: "ui/focus_vision_panel" }
    ]

    property var diagnosticCategories: [
        { label: qsTr("System Snapshot"), category: "system" },
        { label: qsTr("Process Trace"), category: "process" },
        { label: qsTr("Device Telemetry"), category: "device" },
        { label: qsTr("Vision Metrics"), category: "vision" },
        { label: qsTr("UI Layout Dump"), category: "ui" }
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
            window.appendLog("API -> " + endpoint + " " + JSON.stringify(options))
        }
    }

    onUiActionRequested: {
        if (window.autoLogRequests) {
            window.appendLog("UI -> " + actionId + " " + JSON.stringify(options))
        }
    }

    onRefreshUiStateRequested: {
        if (window.autoLogRequests) {
            window.appendLog("UI refresh requested")
        }
    }

    onDiagnosticsRequested: {
        if (window.autoLogRequests) {
            window.appendLog("Diagnostics -> " + category)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        GroupBox {
            title: qsTr("API Connection")
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Label {
                        text: qsTr("Base URL")
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
                        text: qsTr("Apply")
                        onClicked: window.baseUrl = baseUrlField.text
                    }

                    Switch {
                        id: logSwitch
                        checked: window.autoLogRequests
                        text: qsTr("Auto Log")
                        onToggled: window.autoLogRequests = checked
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Button {
                        text: qsTr("Ping API")
                        onClicked: window.apiCallRequested("status/ping", {
                            method: "GET",
                            baseUrl: window.baseUrl
                        })
                    }

                    Button {
                        text: qsTr("Health Check")
                        onClicked: window.apiCallRequested("status/health", {
                            method: "GET",
                            baseUrl: window.baseUrl
                        })
                    }

                    Button {
                        text: qsTr("Reload Config")
                        onClicked: window.apiCallRequested("config/reload", {
                            method: "POST",
                            baseUrl: window.baseUrl
                        })
                    }

                    Button {
                        text: qsTr("List Jobs")
                        onClicked: window.apiCallRequested("jobs/active", {
                            method: "GET",
                            baseUrl: window.baseUrl
                        })
                    }

                    Item {
                        Layout.fillWidth: true
                    }

                    Button {
                        text: qsTr("Refresh UI State")
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
                    title: qsTr("System Controls")
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
                    title: qsTr("Process Controls")
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
                    title: qsTr("Device Controls")
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
                    title: qsTr("Vision Controls")
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
                    title: qsTr("UI Actions")
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
                    title: qsTr("Diagnostics Snapshots")
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
                    title: qsTr("Custom API Call")
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
                                placeholderText: "/custom/endpoint"
                            }

                            Button {
                                text: qsTr("Send")
                                onClicked: {
                                    var body = {}
                                    var raw = payloadArea.text.trim()
                                    if (raw.length > 0) {
                                        try {
                                            body = JSON.parse(raw)
                                        } catch (error) {
                                            window.appendLog("Invalid JSON payload: " + error)
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
                        text: qsTr("Activity Log")
                        font.bold: true
                    }

                    Item {
                        Layout.fillWidth: true
                    }

                    Button {
                        text: qsTr("Copy Latest")
                        onClicked: {
                            if (logModel.count > 0) {
                                Qt.application.clipboard.text = logModel.get(0).message
                                window.appendLog("Copied latest entry to clipboard")
                            }
                        }
                    }

                    Button {
                        text: qsTr("Clear Log")
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
