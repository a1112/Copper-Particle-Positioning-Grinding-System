import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base"
import "." as CodeViews
import "../../datas" as Datas
import "../../cores" as Cores

Rectangle {
 readonly property bool isCurrent: index === Datas.CodeDatas.currentIndex
 readonly property bool isPast: index < Datas.CodeDatas.currentIndex
 width: list.width
 height: 32
 radius: 6
 color: isCurrent ? Qt.tint(Cores.CoreStyle.accent, "#22000000")
         : (isPast ? Qt.tint(Cores.CoreStyle.success, "#15000000") : "transparent")
 border.width: isCurrent ? 1.2 : 0
 border.color: isCurrent ? Cores.CoreStyle.accent : "transparent"

 Behavior on color { ColorAnimation { duration: 150 } }
 Behavior on border.color { ColorAnimation { duration: 150 } }

 RowLayout {
   anchors.fill: parent
   anchors.margins: 8
   spacing: 10

   Rectangle {
     width: 36
     height: 22
     radius: 4
     color: isCurrent ? Cores.CoreStyle.accent :
            (isPast ? Qt.tint(Cores.CoreStyle.success, "#33000000") : Cores.CoreStyle.surface)
     Label {
       anchors.centerIn: parent
       text: model.idx
       color: isCurrent ? "#000000" : Cores.CoreStyle.text
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
     font.bold: isCurrent
     Layout.preferredWidth: 78
     horizontalAlignment: Text.AlignHCenter
   }
 }
}

