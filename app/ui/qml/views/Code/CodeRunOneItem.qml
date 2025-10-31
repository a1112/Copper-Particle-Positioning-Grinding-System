import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base"
import "." as CodeViews
import "../../datas" as Datas
import "../../cores" as Cores

ItemDelegate {
    id: delegateItem
    readonly property bool isCurrent: index === Datas.CodeDatas.currentIndex
    readonly property bool isPast: index < Datas.CodeDatas.currentIndex

    width: list.width
    height: 32

     Rectangle {
         anchors.fill: parent
        id: backgroundRect

        radius: 6
        color: delegateItem.isCurrent
               ? Qt.tint(Cores.CoreStyle.accent, "#22000000")
               : (delegateItem.isPast
                  ? Qt.tint(Cores.CoreStyle.success, "#15000000")
                  : "transparent")
        border.width: delegateItem.isCurrent ? 1.2 : 0
        border.color: delegateItem.isCurrent ? Cores.CoreStyle.accent : "transparent"
        opacity: delegateItem.hovered || delegateItem.isCurrent ? 0.45 : (delegateItem.isPast ? 0.3 : 0.2)

        Behavior on color { ColorAnimation { duration: 120 } }
        Behavior on border.color { ColorAnimation { duration: 120 } }
        Behavior on opacity { NumberAnimation { duration: 120 } }

    }

     RowLayout {
        anchors.fill: parent
        anchors.margins: 1
        spacing: 10

        Rectangle {
            width: 36
            height: 22
            radius: 4
            color: delegateItem.isCurrent
                   ? Cores.CoreStyle.accent
                   : (delegateItem.isPast
                      ? Qt.tint(Cores.CoreStyle.success, "#33000000")
                      : Cores.CoreStyle.surface)

            Label {
                anchors.centerIn: parent
                text: model.idx
                color: delegateItem.isCurrent ? "#000000" : Cores.CoreStyle.text
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
            font.bold: delegateItem.isCurrent
            Layout.preferredWidth: 78
            horizontalAlignment: Text.AlignHCenter
        }
    }

}
