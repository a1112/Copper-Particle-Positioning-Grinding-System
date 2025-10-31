import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../Api" as Api
import "../../components/Base" as Base
Popup {
    id: root
    modal: true
    dim: true
    focus: true
    anchors.centerIn: parent
    width: parent ? parent.width * 0.85 : 960
    height: parent ? parent.height * 0.85 : 600
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

    property var settingsData: ({
        job_sections: [],
        calibration_sections: [],
        machine_sections: [],
        safety_sections: [],
        monitor_defaults: [],
        tool_table: [],
        sources: {}
    })
    property bool loading: false
    property string errorText: ""
    property int currentIndex: 0

    function _safeObject(value) {
        if (value === undefined)
            return {}
        if (value === null)
            return {}
        return value
    }

    function _safeArray(value) {
        if (!Array.isArray(value))
            return []
        return value
    }

    function _safeString(value) {
        if (value === undefined)
            return ""
        if (value === null)
            return ""
        return value
    }

    function _preferred(value, fallback) {
        if (value === undefined)
            return fallback
        if (value === null)
            return fallback
        if (value === "")
            return fallback
        return value
    }

    background: Rectangle {
        color: "#1a1d23"
        radius: 12
        border.color: "#2b2f36"
        border.width: 1
    }

    function loadSettings() {
        loading = true
        errorText = ""
        try {
            Api.ApiClient.configSettings(
                        function(resp) {
                            settingsData = root._safeObject(resp)
                            loading = false
                        },
                        function(status, message) {
                            loading = false
                            errorText = "加载失败: " + root._preferred(message, status)
                        })
        } catch (err) {
            loading = false
            errorText = "加载失败: " + err
        }
    }

    Component.onCompleted: loadSettings()

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            SettingPageTitle {
                Layout.alignment: Qt.AlignVCenter
            }

            Item { Layout.fillWidth: true }

            Label {
                text: settingsData && settingsData.sources
                      ? ("源文件: " + root._safeString(settingsData.sources.job) + " | " + root._safeString(settingsData.sources.machine))
                      : ""
                color: "#9aa0ac"
                wrapMode: Text.WrapAnywhere
                maximumLineCount: 2
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredWidth: 420
                visible: text.length > 0
            }

            Button {
                text: loading ? "刷新中…" : "刷新"
                enabled: !loading
                Layout.alignment: Qt.AlignVCenter
                onClicked: loadSettings()
            }

            Button {
                text: qsTr("关闭")
                Layout.alignment: Qt.AlignVCenter
                onClicked: root.close()
            }
        }

        Label {
            text: qsTr("提示：设置中心会同步读取配置文件，大多数参数可直接在此界面修改；每项说明提示了修改影响范围。")
            color: "#91a0ba"
            wrapMode: Text.Wrap
            Layout.fillWidth: true
        }

        SettingPageHead {
            Layout.alignment: Qt.AlignRight
            currentIndex: root.currentIndex
            onCurrentIndexChanged: root.currentIndex = currentIndex
        }
        SettingBody{
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: root.currentIndex
        }

    }

    BusyIndicator {
        anchors.centerIn: parent
        visible: root.loading
        running: root.loading
        z: 2
    }

    Label {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 12
        color: "#ff8080"
        text: root.errorText
        visible: root.errorText.length > 0
        z: 2
    }
}
