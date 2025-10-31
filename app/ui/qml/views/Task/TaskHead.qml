import QtQuick


import QtQuick.Controls
import QtQuick.Layouts

import "../../Api" as Api
import "../../cores" as Cores
import "../../components/btns" as Btns
import "../../components/Card"
import "../../components/Base" as Base
import "../../datas" as Datas
import "../Base"


CardHead {
  Layout.fillWidth: true
  RowLayout {
    anchors.fill: parent
    spacing: 4
    Item{
      width: 1
      height: 1
    }
    Base.CardTitleLabel {
      text: qsTr("任务流程")

    }
    Item{
      Layout.fillWidth: true
      height: 1
    }
  }
}


