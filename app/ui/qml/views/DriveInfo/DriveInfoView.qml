import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base"
import "../../cores" as Cores
import "../../Sockets" as Sockets
import "../Charts" as Charts

// 驱动信息视图：上方关键状态/位置，下方转速/扭矩曲线
BaseCard {
    id: root

    // 简单缓存曲线数据（基于 WS 推送）
    property var rpmSeries: []       // 主轴转速 rpm
    property var torqueSeries: []    // 主轴扭矩 N·m（若服务端提供 spindle_torque 字段则显示）
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

        // 顶部关键信息
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6

            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                Label { text: "连接"; color: Cores.CoreStyle.muted; Layout.preferredWidth: 56 }
                Rectangle { width: 10; height: 10; radius: 5
                    color: Sockets.Sockets.connected ? Cores.CoreStyle.success : Cores.CoreStyle.danger }
                Label {
                    text: Sockets.Sockets.connected ? "已连接" : "未连接"
                    color: Sockets.Sockets.connected ? Cores.CoreStyle.success : Cores.CoreStyle.danger
                }
                Item { Layout.fillWidth: true }
                Label {
                    text: "状态: " + ((Sockets.Sockets.lastMessage && Sockets.Sockets.lastMessage.state) || "-")
                    color: Cores.CoreStyle.text
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 16
                Label { text: "位置"; color: Cores.CoreStyle.muted; Layout.preferredWidth: 56 }
                Label {
                    readonly property var pos: (Sockets.Sockets.lastMessage && Sockets.Sockets.lastMessage.position) || {}
                    text: `X:${Number(pos.x||0).toFixed(2)}  Y:${Number(pos.y||0).toFixed(2)}  Z:${Number(pos.z||0).toFixed(2)}  θ:${Number(pos.theta||0).toFixed(2)}`
                    color: Cores.CoreStyle.text
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 16
                Label { text: "主轴转速"; color: Cores.CoreStyle.muted; Layout.preferredWidth: 56 }
                Label {
                    text: `${Number((Sockets.Sockets.lastMessage && Sockets.Sockets.lastMessage.spindle_rpm) || 0).toFixed(0)} rpm`
                    color: Cores.CoreStyle.accent
                }
                Item { Layout.fillWidth: true }
                Label { text: "扭矩"; color: Cores.CoreStyle.muted; Layout.preferredWidth: 40 }
                Label {
                    readonly property var tq: (Sockets.Sockets.lastMessage && (Sockets.Sockets.lastMessage.spindle_torque))
                    text: (tq===undefined||tq===null? "-" : `${Number(tq).toFixed(2)} N·m`)
                    color: Cores.CoreStyle.text
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: Cores.CoreStyle.border }
        }

        // 曲线区：上 转速 / 下 扭矩
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

    // 订阅 WS 消息：提取转速/扭矩、触发重绘
    Connections {
        target: Sockets.Sockets
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
