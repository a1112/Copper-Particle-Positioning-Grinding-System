import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../cores" as Cores
import "../../components/Base"
import "../../components/btns"
import "../../Sockets" as Sockets

Item {
  id: root
  height: 50
  Layout.fillWidth: true


  Pane {
    anchors.fill: parent
    background: Rectangle { color: Cores.CoreStyle.surface; border.color: Cores.CoreStyle.border }
  }

  // Running state from status socket
  readonly property bool isRunning: (Sockets.StatusSocket.lastMessage && Sockets.StatusSocket.lastMessage.state) === "RUNNING"

  RowLayout {
    anchors.fill: parent
    spacing: 18

    Row { // logo + title icon
      IconView { height: root.height; width: height*4;  }
      // IconLabel { anchors.verticalCenter: parent.verticalCenter }
    }

    ViewChangeTabView {}
    FillItem {}
    TitleLabel {}
    FillItem {}
    RunModelSelect{}
    FillItem {}
    EstopBtn{}

    DateTimeView { Layout.alignment: Qt.AlignVCenter }
    ItemDelegateButtonBase { source: Cores.CoreStyle.getIconSource("tool.png"); height: root.height; width: height*2; onClicked: settingsPage.open() }
    ItemDelegateButtonBase { source: Cores.CoreStyle.getIconSource("setting.png"); height: root.height; width: height*2; onClicked: settingsDrawer.open() }
    Item { width: 10; height: 2 }
  }
}

