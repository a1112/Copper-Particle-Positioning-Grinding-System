import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../Api" as Api

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
                            settingsData = resp || {}
                            loading = false
                        },
                        function(status, message) {
                            loading = false
                            errorText = "加载失败: " + (message || status)
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
                      ? ("源文件: " + (settingsData.sources.job || "") + " | " + (settingsData.sources.machine || ""))
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
                text: "关闭"
                Layout.alignment: Qt.AlignVCenter
                onClicked: root.close()
            }
        }

        Label {
            text: "提示：设置中心会同步读取配置文件，大多数参数可直接在此界面修改；每项说明提示了修改影响范围。"
            color: "#91a0ba"
            wrapMode: Text.Wrap
            Layout.fillWidth: true
        }

        SettingPageHead {
            Layout.alignment: Qt.AlignRight
            currentIndex: root.currentIndex
            onCurrentIndexChanged: root.currentIndex = currentIndex
        }

        StackLayout {
            id: stack
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: root.currentIndex

            ScrollView {
                clip: true
                Layout.fillWidth: true
                Layout.fillHeight: true
                contentItem: ColumnLayout {
                    width: parent.width - 6
                    spacing: 16
                    SettingSectionList {
                        title: "任务配置"
                        sections: settingsData.job_sections || []
                    }
                    Label {
                        visible: !root.loading && (settingsData.job_sections || []).length === 0
                        text: "未读取到任务配置。"
                        color: "#a0a6b4"
                    }
                    Item { Layout.fillWidth: true; Layout.fillHeight: true }
                }
            }

            ScrollView {
                clip: true
                Layout.fillWidth: true
                Layout.fillHeight: true
                contentItem: ColumnLayout {
                    width: parent.width - 6
                    spacing: 16
                    SettingSectionList {
                        title: "标定与工件坐标"
                        sections: (settingsData.calibration_sections || [])
                    }
                    SettingSectionList {
                        title: "机台运动参数"
                        sections: settingsData.machine_sections || []
                    }
                    SettingSectionList {
                        title: "安全互锁"
                        sections: settingsData.safety_sections || []
                    }
                    SettingSectionList {
                        title: "监控默认阈值"
                        sections: (settingsData.monitor_defaults && settingsData.monitor_defaults.length > 0)
                                  ? [{ "name": "monitor_defaults", "items": settingsData.monitor_defaults }]
                                  : []
                    }
                    Label {
                        visible: !root.loading
                                 && (settingsData.calibration_sections || []).length === 0
                                 && (settingsData.machine_sections || []).length === 0
                                 && (settingsData.safety_sections || []).length === 0
                                 && (!settingsData.monitor_defaults || settingsData.monitor_defaults.length === 0)
                        text: "未读取到机台配置。"
                        color: "#a0a6b4"
                    }
                    Item { Layout.fillWidth: true; Layout.fillHeight: true }
                }
            }

            ScrollView {
                clip: true
                Layout.fillWidth: true
                Layout.fillHeight: true
                contentItem: Column {
                    width: parent.width - 6
                    spacing: 12

                    Rectangle {
                        width: parent.width
                        height: 36
                        radius: 6
                        color: "#232832"
                        border.color: "#303541"

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 16

                            Label { text: "编号"; font.bold: true; color: "#9ad"; Layout.preferredWidth: 80 }
                            Label { text: "名称"; font.bold: true; color: "#9ad"; Layout.fillWidth: true }
                            Label { text: "直径"; font.bold: true; color: "#9ad"; Layout.preferredWidth: 80; horizontalAlignment: Qt.AlignRight }
                            Label { text: "长度"; font.bold: true; color: "#9ad"; Layout.preferredWidth: 80; horizontalAlignment: Qt.AlignRight }
                        }
                    }

                    Repeater {
                        model: settingsData.tool_table || []
                        delegate: Rectangle {
                            width: parent.width
                            height: 40
                            radius: 4
                            color: index % 2 === 0 ? "#1e222b" : "#202734"
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 8
                                spacing: 16

                                Label { text: modelData.code; font.bold: true; color: "#d0d6ff"; Layout.preferredWidth: 80 }
                                Label { text: modelData.name; color: "#e0e6ef"; Layout.fillWidth: true; elide: Text.ElideRight }
                                Label {
                                    text: modelData.diameter
                                    color: "#e0e6ef"
                                    horizontalAlignment: Qt.AlignRight
                                    Layout.preferredWidth: 80
                                }
                                Label {
                                    text: modelData.length
                                    color: "#e0e6ef"
                                    horizontalAlignment: Qt.AlignRight
                                    Layout.preferredWidth: 80
                                }
                            }
                        }
                    }

                    Label {
                        visible: (settingsData.tool_table || []).length === 0
                        text: "未读取到刀具表。"
                        color: "#a0a6b4"
                    }
                }
            }
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
