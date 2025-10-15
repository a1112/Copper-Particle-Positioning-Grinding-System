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

  // Global shortcuts: Ctrl+E / Ctrl+Shift+E -> open E-STOP confirmation; Enter/Return to confirm
  Shortcut { sequence: "Ctrl+E"; onActivated: confirmEstop.open() }
  Shortcut { sequence: "Ctrl+Shift+E"; onActivated: confirmEstop.open() }
  Shortcut { sequence: "Enter"; onActivated: if (confirmEstop.visible) confirmEstop.accept() }
  Shortcut { sequence: "Return"; onActivated: if (confirmEstop.visible) confirmEstop.accept() }

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

    // Emergency Stop (left of time)
    Rectangle {
      id: estopBtn
      Layout.alignment: Qt.AlignVCenter
      height: Math.max(36, parent.height*0.8)
      width: height * 2.4
      radius: 8
      color: root.isRunning ? Cores.CoreStyle.danger : Cores.CoreStyle.muted
      border.color: root.isRunning ? "#b91c1c" : Cores.CoreStyle.border
      border.width: 1
      opacity: root.isRunning ? 1.0 : 0.5
      RowLayout { anchors.fill: parent; anchors.margins: 6; spacing: 6
        Image { source: Cores.CoreStyle.getIconSource("close.png"); fillMode: Image.PreserveAspectFit; Layout.preferredWidth: estopBtn.height*0.6; Layout.preferredHeight: estopBtn.height*0.6 }
        Label { text: "急停"; color: "white"; font.bold: true }
      }
      MouseArea { anchors.fill: parent; enabled: root.isRunning; onClicked: confirmEstop.open() }
    }

    Dialog {
      id: confirmEstop
      modal: true
      anchors.centerIn: Overlay.overlay
      title: "确认急停"
      standardButtons: Dialog.Yes | Dialog.Cancel
      contentItem: Column {
        spacing: 8; padding: 12
        Label { wrapMode: Text.WordWrap; text: "是否立即执行急停？此操作会立即中断动作" }
      }
      onAccepted: { Cores.CoreControl.estop(); close() }
    }

    DateTimeView { Layout.alignment: Qt.AlignVCenter }
    ItemDelegateButtonBase { source: Cores.CoreStyle.getIconSource("tool.png"); height: root.height; width: height*2; onClicked: settingsPage.open() }
    ItemDelegateButtonBase { source: Cores.CoreStyle.getIconSource("setting.png"); height: root.height; width: height*2; onClicked: settingsDrawer.open() }
    Item { width: 10; height: 2 }
  }
}

