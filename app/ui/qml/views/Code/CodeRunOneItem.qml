import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base"
import "." as CodeViews
import "../../datas" as Datas
import "../../cores" as Cores

ItemDelegate {
    id: delegateItem
    readonly property bool isRunning: Datas.CodeDatas.runState === "RUNNING"
    readonly property bool isActive: Cores.CoreCutting.activeIndex === index
    readonly property bool isSelected: !isRunning && Cores.CoreCutting.selectedIndex === index
    readonly property bool isPast: (Cores.CoreCutting.activeIndex >= 0) && (index < Cores.CoreCutting.activeIndex)
    width: list.width
    height: 32
    hoverEnabled: true
    focusPolicy: Qt.NoFocus
    onClicked: {
        if (!isRunning)
            Cores.CoreCutting.selectIndex(index)
    }

    Rectangle {
        id: backgroundRect
        anchors.fill: parent
        radius: 6
        color: delegateItem.isActive
               ? Qt.tint(Cores.CoreStyle.accent, "#22000000")
               : (delegateItem.isSelected
                  ? Qt.tint(Cores.CoreStyle.info, "#15000000")
                  : (delegateItem.isPast
                     ? Qt.tint(Cores.CoreStyle.success, "#15000000")
                     : "transparent"))
        border.width: delegateItem.isActive || delegateItem.isSelected ? 1.2 : 0
        border.color: delegateItem.isActive ? Cores.CoreStyle.accent
                     : (delegateItem.isSelected ? Cores.CoreStyle.info : "transparent")
        opacity: delegateItem.isActive ? 0.55
                 : (delegateItem.isSelected ? 0.42
                    : (delegateItem.hovered ? 0.35
                       : (delegateItem.isPast ? 0.28 : 0.18)))

        Behavior on color { ColorAnimation { duration: 120 } }
        Behavior on border.color { ColorAnimation { duration: 120 } }
        Behavior on opacity { NumberAnimation { duration: 120 } }
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 2
        spacing: 10
        Rectangle {
            width: 36
            height: 22
            radius: 4
            color: delegateItem.isActive
                   ? Cores.CoreStyle.accent
                   : (delegateItem.isPast
                      ? Qt.tint(Cores.CoreStyle.success, "#33000000")
                      : Cores.CoreStyle.surface)

            Label {
                anchors.centerIn: parent
                text: model.idx
                color: delegateItem.isActive ? "#000000" : Cores.CoreStyle.text
                font.family: "monospace"
            }
        }

        Label {
            Layout.fillWidth: true
            text: model.text
            color: Cores.CoreStyle.text
            font.family: "monospace"
            horizontalAlignment: Text.AlignLeft
            elide: Text.ElideRight
        }

        Label {
            text: model.status
            color: root.statusColor(model.status)
            font.bold: delegateItem.isActive || delegateItem.isSelected
            Layout.preferredWidth: 78
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
