import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base"
import "../../cores" as Cores
import "../../datas" as Datas
import "../Charts" as Charts

BaseCard {
    id: root

    property var rpmSeries: []
    property var torqueSeries: []
    readonly property int maxPoints: 240

    function _pushSeries(arr, v) {
        if (v === undefined || v === null || isNaN(v)) return
        arr.push(Number(v))
        if (arr.length > maxPoints) arr.shift()
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Connection & basic info
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6

            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                Label { text: "连接"; color: Cores.CoreStyle.muted; Layout.preferredWidth: 56 }
                Rectangle { width: 10; height: 10; radius: 5;
                    color: Datas.StatusDatas.connected ? Cores.CoreStyle.success : Cores.CoreStyle.danger }
                Label {
                    text: (Datas.StatusDatas.connected ? "已连接" : "未连接")
                    color: Datas.StatusDatas.connected ? Cores.CoreStyle.success : Cores.CoreStyle.danger
                }
                Item { Layout.fillWidth: true }
                Label {
                    text: "状态: " + ((Datas.StatusDatas.lastMessage && Datas.StatusDatas.lastMessage.state) || "-")
                    color: Cores.CoreStyle.text
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 16
                Label { text: "位置"; color: Cores.CoreStyle.muted; Layout.preferredWidth: 56 }
                Label {
                    readonly property var pos: (Datas.StatusDatas.lastMessage && Datas.StatusDatas.lastMessage.position) || {}
                    text: `X:${Number(pos.x||0).toFixed(2)}  Y:${Number(pos.y||0).toFixed(2)}  Z:${Number(pos.z||0).toFixed(2)}  Theta:${Number(pos.theta||0).toFixed(2)}`
                    color: Cores.CoreStyle.text
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 16
                Label { text: "主轴转速"; color: Cores.CoreStyle.muted; Layout.preferredWidth: 72 }
                Label {
                    text: `${Number((Datas.StatusDatas.lastMessage && Datas.StatusDatas.lastMessage.spindle_rpm) || 0).toFixed(0)} rpm`
                    color: Cores.CoreStyle.accent
                }
                Item { Layout.fillWidth: true }
                Label { text: "扭矩"; color: Cores.CoreStyle.muted; Layout.preferredWidth: 56 }
                Label {
                    readonly property var tq: (Datas.StatusDatas.lastMessage && (Datas.StatusDatas.lastMessage.spindle_torque))
                    text: (tq===undefined||tq===null? "-" : `${Number(tq).toFixed(2)} N*m`)
                    color: Cores.CoreStyle.text
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: Cores.CoreStyle.border }
        }

        // Charts: RPM / Torque
        Charts.RpmChart {
            id: rpmChart
            Layout.fillWidth: true
            Layout.preferredHeight: 140
            series: root.rpmSeries
        }

        Charts.TorqueChart {
            id: tqChart
            Layout.fillWidth: true
            Layout.preferredHeight: 140
            series: root.torqueSeries
        }

        Item { Layout.fillHeight: true }
    }

    Connections {
        target: Datas.StatusDatas
        function onMessageReceived(p) {
            try {
                if (!p) return
                root._pushSeries(root.rpmSeries, p.spindle_rpm)
                if (p.spindle_torque !== undefined) root._pushSeries(root.torqueSeries, p.spindle_torque)
                rpmChart.repaint()
                tqChart.repaint()
            } catch(e) { /* ignore */ }
        }
    }
}

