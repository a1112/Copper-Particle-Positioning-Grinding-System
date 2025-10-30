import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../Api" as Api
import "../../components/Base" as Base

StackLayout {
    id: stack

    ScrollView {
        clip: true
        Layout.fillWidth: true
        Layout.fillHeight: true
        contentItem: ColumnLayout {
            width: parent.width - 6
            spacing: 16
            SettingSectionList {
                title: "任务配置"
                sections: root._safeArray(settingsData.job_sections)
            }
            Label {
                visible: !root.loading && root._safeArray(settingsData.job_sections).length === 0
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
                sections: root._safeArray(settingsData.calibration_sections)
            }
            SettingSectionList {
                title: "机台运动参数"
                sections: root._safeArray(settingsData.machine_sections)
            }
            SettingSectionList {
                title: "安全互锁"
                sections: root._safeArray(settingsData.safety_sections)
            }
            SettingSectionList {
                title: "监控默认阈值"
                sections: (settingsData.monitor_defaults && settingsData.monitor_defaults.length > 0)
                          ? [{ "name": "monitor_defaults", "items": settingsData.monitor_defaults }]
                          : []
            }
            Label {
                visible: !root.loading
                         && root._safeArray(settingsData.calibration_sections).length === 0
                         && root._safeArray(settingsData.machine_sections).length === 0
                         && root._safeArray(settingsData.safety_sections).length === 0
                         && root._safeArray(settingsData.monitor_defaults).length === 0
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
                model: root._safeArray(settingsData.tool_table)
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
                visible: root._safeArray(settingsData.tool_table).length === 0
                text: "未读取到刀具表。"
                color: "#a0a6b4"
            }
        }
    }

}
