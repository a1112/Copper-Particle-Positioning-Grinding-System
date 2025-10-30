import QtQuick


import QtQuick.Controls
import QtQuick.Layouts

import "../../Api" as Api
import "../../cores" as Cores
import "../../components/btns" as Btns
import "../../datas" as Datas
import "../Base"


Item {
  height:Cores.CoreStyle.cardHeadHeight
  Layout.fillWidth: true

  RowLayout {
    Layout.fillWidth: true
    spacing: 4
    Item{
      Layout.fillWidth: true
      height: 1
    }
    Label {
      text: qsTr("任务流程")
      font.pixelSize: 14
      font.bold: true
      color: Cores.CoreStyle.text
    }
    Item{
      Layout.fillWidth: true
      height: 1
    }
  }
}


