import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import "../../cores" as Cores
import "../../components/Base"
import "../../components/btns"
import "../../datas" as Datas
import "../../menu" as Menu
import "."

Item {
  id: root
  height: 50
  Layout.fillWidth: true
  property Item appWindow: null
  property Item dataDialog: null

  Pane {
    anchors.fill: parent
    background: Rectangle { color: Cores.CoreStyle.surface; border.color: Cores.CoreStyle.border }
  }

  // Running state from status socket
  readonly property bool isRunning: (Datas.StatusDatas.lastMessage && Datas.StatusDatas.lastMessage.state) === "RUNNING"

  RowLayout {
    anchors.fill: parent
    spacing: 18

    Row { // logo + title icon
      spacing: 2
      height: parent.height
      Item{
      width: 15
      height: 1
      }
      ItemDelegateButtonBase {
        id: mainMenuButton
        height: parent.height
        width: height
        tipText: qsTr("主菜单")
        source: Cores.CoreStyle.getIconSource("Menu.png")
        onClicked: {
          headMainMen.popup(mainMenuButton, 0, mainMenuButton.height)
        }
      }

      IconView { height: root.height; width: height * 4 }
      // IconLabel { anchors.verticalCenter: parent.verticalCenter }
    }

    ViewChangeTabView {}
    FillItem {}

    TitleLabel {}
    FillItem {}
    RunModelSelect {}
    FillItem {}
    EstopBtn {}
    CaptureButton {}
    SemiAutoStartBtn { running: root.isRunning }

    DateTimeView { Layout.alignment: Qt.AlignVCenter }
    ItemDelegateButtonBase {
      source: Cores.CoreStyle.getIconSource("tool.png")
      height: root.height
      width: height * 2
      onClicked: settingsPage.open()
    }
    ItemDelegateButtonBase {
      source: Cores.CoreStyle.getIconSource("setting.png")
      height: root.height
      width: height * 2
      onClicked: settingsDrawer.open()
    }
    Item { width: 10; height: 2 }
  }

  Menu.MainMenu {
    id: headMainMen
    dataDialog: root.dataDialog
  }
}
