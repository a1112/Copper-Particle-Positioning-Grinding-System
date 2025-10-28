import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../cores" as Cores
import "../../datas" as Datas
import "../../works" as Works
import "../../Api" as Api

Rectangle {
  Layout.fillWidth: true
  radius: 10
  color: "#131c2b"
  border.color: "#1f2a3b"
  anchors.margins: 0
  height: 50
  required property var statePageCore
  RowLayout {
    id:row
    anchors.fill: parent
    anchors.margins: 10
    spacing: 15

    RowLayout {
      spacing: 4
      Label { text: qsTr("工件信息"); color: Cores.CoreStyle.muted; font.pixelSize: 12 }
      Label { text: statePageCore.workpieceLabel(); color: Cores.CoreStyle.text; font.pixelSize: 18; font.bold: true }
    }

    RowLayout {
      spacing: 4
      Label { text: qsTr("最新记录ID"); color: Cores.CoreStyle.muted; font.pixelSize: 12 }
      Label { text: Datas.TaskDatas.latestRecordId ? ("#" + Datas.TaskDatas.latestRecordId) : "-"; color: Cores.CoreStyle.text; font.pixelSize: 18; font.bold: true }
    }

    RowLayout {
      spacing: 4
      Label { text: qsTr("状态"); color: Cores.CoreStyle.muted; font.pixelSize: 12 }
      Label { text: statePageCore.safeText(statePageCore.statusSnapshot.state, qsTr("待机")); color: statePageCore.statusColor(statePageCore.statusSnapshot.state); font.pixelSize: 18; font.bold: true }
    }

    RowLayout {
      spacing: 4
      Label { text: qsTr("运行模式"); color: Cores.CoreStyle.muted; font.pixelSize: 12 }
      Label { text: statePageCore.safeText(statePageCore.statusSnapshot.run_mode || statePageCore.statusSnapshot.runMode, "-"); color: Cores.CoreStyle.info; font.pixelSize: 18; font.bold: true }
    }

    Item { Layout.fillWidth: true }
  }
}

