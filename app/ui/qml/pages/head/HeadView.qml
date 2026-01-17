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

  readonly property var appWindow: Window.window
  readonly property bool isFullScreen: appWindow ? appWindow.visibility === Window.FullScreen : false
  readonly property bool framelessEnabled: Cores.CoreSettings ? Cores.CoreSettings.framelessWindow : false

  function toggleFullScreen() {
    if (!appWindow)
      return
    if (appWindow.toggleFullScreen) {
      appWindow.toggleFullScreen()
      return
    }
    if (appWindow.visibility === Window.FullScreen) {
      appWindow.showNormal()
    } else {
      appWindow.showFullScreen()
    }
  }

  Pane {
    anchors.fill: parent
    background: Rectangle { color: Cores.CoreStyle.surface; border.color: Cores.CoreStyle.border }
  }

  // Drag area for frameless window
  MouseArea {
    id: windowDragArea
    anchors.fill: parent
    visible: root.framelessEnabled
    enabled: root.framelessEnabled
    hoverEnabled: true
    acceptedButtons: Qt.LeftButton
    cursorShape: Qt.SizeAllCursor
    onPressed: {
      if (!appWindow)
        return
      if (appWindow.visibility === Window.FullScreen)
        return
      if (appWindow.visibility === Window.Maximized) {
        var ratio = root.width > 0 ? mouse.x / root.width : 0.5
        ratio = Math.min(Math.max(ratio, 0), 1)
        appWindow.showNormal()
        appWindow.x = mouse.screenX - appWindow.width * ratio
        appWindow.y = mouse.screenY - mouse.y
      }
      if (appWindow.startSystemMove)
        appWindow.startSystemMove()
    }
    onDoubleClicked: {
      if (!appWindow)
        return
      root.toggleFullScreen()
    }
  }

  // Running state from status socket
  readonly property bool isRunning: Datas.StatusDatas.forceEnableControls|(Datas.StatusDatas.lastMessage && Datas.StatusDatas.lastMessage.state) === "RUNNING"

  RowLayout {
    anchors.fill: parent
    z: 1
    spacing: 18

    Row { // logo + title icon
      spacing: 2
      height: parent.height
      Item{
      width: 15
      height: 1
      }
      ItemDelegateButtonBase {
        id: historyDrawerButton
        height: parent.height
        width: height
        tipText: qsTr("历史记录")
        source: Cores.CoreStyle.getIconSource("arrow-next.png")
        onClicked: {
          if (historyDrawer && historyDrawer.open)
            historyDrawer.open()
        }
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
    EstopBtn {
      estopEnable:Cores.CoreButtonState.estopEnable
    }
    CaptureButton {}
    SemiAutoStartBtn { running: root.isRunning }

    DateTimeView { Layout.alignment: Qt.AlignVCenter }

    ItemDelegateButtonBase {
      source: Cores.CoreStyle.getIconSource("msg.png")
      height: root.height
      width: height * 2
      onClicked: {
        statePage.open()
      }
    }
    ItemDelegateButtonBase {
      source: Cores.CoreStyle.getIconSource("tool.png")
      height: root.height
      width: height * 2
      onClicked: {
        settingsPage.open()
      }
    }
    ItemDelegateButtonBase {
      source: Cores.CoreStyle.getIconSource("setting.png")
      height: root.height
      width: height * 2
      onClicked: {
        settingsDrawer.open()
      }
    }
    Row {
      spacing: 6
      height: parent.height
      Layout.alignment: Qt.AlignVCenter
      visible: root.framelessEnabled
      enabled: root.framelessEnabled
      ItemDelegate {
        id: minimizeButton
        height: parent.height
        width: height
        padding: 0
        hoverEnabled: true
        property string tipText: qsTr("\u6700\u5c0f\u5316")
        ToolTip.visible: tipText !== "" && hovered
        ToolTip.text: tipText
        enabled: !!root.appWindow
        onClicked: {
          if (root.appWindow)
            root.appWindow.showMinimized()
        }
        contentItem: Item {
          anchors.fill: parent
          Rectangle {
            anchors.centerIn: parent
            width: parent.width * 0.45
            height: 2
            radius: 1
            color: minimizeButton.hovered ? Cores.CoreStyle.text : Cores.CoreStyle.muted
          }
        }
      }
      WindowModelChangeButton {
        height: parent.height
        width: height
        shouMaxIcon: !root.isFullScreen
        enabled: !!root.appWindow
        onClicked: root.toggleFullScreen()
      }
      ItemDelegate {
        id: closeButton
        height: parent.height
        width: height
        padding: 0
        hoverEnabled: true
        property string tipText: qsTr("\u5173\u95ed")
        ToolTip.visible: tipText !== "" && hovered
        ToolTip.text: tipText
        enabled: !!root.appWindow
        onClicked: {
          if (root.appWindow)
            root.appWindow.close()
        }
        contentItem: Item {
          anchors.centerIn: parent
          width: parent.width * 0.5
          height: width
          Rectangle {
            anchors.centerIn: parent
            width: parent.width
            height: 2
            radius: 1
            color: closeButton.hovered ? Cores.CoreStyle.danger : Cores.CoreStyle.text
            rotation: 45
            transformOrigin: Item.Center
          }
          Rectangle {
            anchors.centerIn: parent
            width: parent.width
            height: 2
            radius: 1
            color: closeButton.hovered ? Cores.CoreStyle.danger : Cores.CoreStyle.text
            rotation: -45
            transformOrigin: Item.Center
          }
        }
      }
    }
    Item { width: 10; height: 2 }
  }

  Menu.MainMenu {
    id: headMainMen
  }
}
