import QtQuick
import QtQuick.Controls.Material
import QtQuick.Layouts
import "../../cores" as Cores
import "../../components/Base"
import "../../components/btns"

Item {
  id: root
  height: 50
  Layout.fillWidth: true

  Pane{
    anchors.fill: parent
    background: Rectangle { color: Cores.CoreStyle.surface; border.color: Cores.CoreStyle.border }  }

  RowLayout{
    anchors.fill: parent
    spacing: 18
    Row{  // 图标区域
      IconView{
        height: root.height
        width: height*2
        source: Cores.CoreStyle.getIconSource("share.png")
      }
      IconLabel{
        anchors.verticalCenter: parent.verticalCenter
      }
    }
    ViewChangeTabView{}

    FillItem{}

    TitleLabel{}

    FillItem{}

    DateTimeView{
      Layout.alignment: Qt.AlignVCenter
    }
    SettingsButton{
      source: Cores.CoreStyle.getIconSource("setting.png")
      height: root.height
      width: height*2
      onClicked:  settingsDrawer.open()
    }
    Item { width: 10; height: 2 }
  }
}

