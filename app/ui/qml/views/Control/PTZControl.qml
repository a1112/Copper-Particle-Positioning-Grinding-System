import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../cores" as Cores
import "../Base"
import "../../components/btns" as Btns
import "../../components/Base"

// 云台手动控制：箭头矩形按钮 + 速度设置
BaseCard {
  id: root

  // 速度 (mm/s)
  property int vFast: 100
  property int vWork: 10
  // 键盘按下状态（用于高亮）
  property bool keyUpHeld: false
  property bool keyDownHeld: false
  property bool keyLeftHeld: false
  property bool keyRightHeld: false

  readonly property bool directControlEnabled: Cores.CoreControl.allowDirectControl
  readonly property bool jogEnabled: Cores.CoreControl.allowJogging

  enabled: directControlEnabled
  Keys.priority: Keys.BeforeItem
  focus: true
  activeFocusOnTab: true

  function jogX(dir, spd) { if (jogEnabled) Cores.CoreControl.jog("x", dir, spd) }
  function jogY(dir, spd) { if (jogEnabled) Cores.CoreControl.jog("y", dir, spd) }
  function keySpeed(ev) { return (ev.modifiers & Qt.ShiftModifier) ? vWork : vFast }

  Keys.onPressed: function(ev) {
    if (!directControlEnabled || !jogEnabled)
      return
    var spd = keySpeed(ev)
    if (ev.key === Qt.Key_Up) { keyUpHeld = true; jogY(1, spd); ev.accepted = true }
    else if (ev.key === Qt.Key_Down) { keyDownHeld = true; jogY(-1, spd); ev.accepted = true }
    else if (ev.key === Qt.Key_Left) { keyLeftHeld = true; jogX(-1, spd); ev.accepted = true }
    else if (ev.key === Qt.Key_Right) { keyRightHeld = true; jogX(1, spd); ev.accepted = true }
  }

  Keys.onReleased: function(ev){
    if (ev.key === Qt.Key_Up) { keyUpHeld = false; ev.accepted = true }
    else if (ev.key === Qt.Key_Down) { keyDownHeld = false; ev.accepted = true }
    else if (ev.key === Qt.Key_Left) { keyLeftHeld = false; ev.accepted = true }
    else if (ev.key === Qt.Key_Right) { keyRightHeld = false; ev.accepted = true }
  }

  // 点击任意处获取焦点以接收键盘事件
  MouseArea { anchors.fill: parent; acceptedButtons: Qt.NoButton; hoverEnabled: true; onEntered: root.forceActiveFocus() }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 2
    spacing: 8

    RowLayout {
      Layout.fillWidth: true
      spacing: 8
      Label { text: qsTr("快速"); color: Cores.CoreStyle.text }
      SpinBoxBase { from: 1; to: 1000; value: root.vFast; enabled: root.directControlEnabled; onValueModified: root.vFast = value; Layout.preferredWidth: 90 }
      Label { text: qsTr("切削"); color: Cores.CoreStyle.text }
      SpinBoxBase { from: 0; to: 200; value: root.vWork; enabled: root.directControlEnabled; onValueModified: root.vWork = value; Layout.preferredWidth: 90 }
      Btns.ActionButton {
        text: qsTr("设置")
        enabled: root.directControlEnabled
        onClicked: Cores.CoreControl.setSpeed(root.vFast, root.vWork)
      }
    }

    RowLayout {
      Layout.fillWidth: true
      Layout.fillHeight: true
      spacing: 16

      Item {
        Layout.fillWidth: true
        Layout.fillHeight: true
        GridLayout {
          id: grid
          columns: 3
          rowSpacing: 8
          columnSpacing: 8
          anchors.centerIn: parent

          Repeater {
            model: [
              ({ label: qsTr("↖"), dx: -1, dy: 1 }),
              ({ label: qsTr("↑"), dx: 0, dy: 1 }),
              ({ label: qsTr("↗"), dx: 1, dy: 1 }),
              ({ label: qsTr("←"), dx: -1, dy: 0 }),
              ({ label: "", dx: 0, dy: 0 }),
              ({ label: qsTr("→"), dx: 1, dy: 0 }),
              ({ label: qsTr("↙"), dx: -1, dy: -1 }),
              ({ label: qsTr("↓"), dx: 0, dy: -1 }),
              ({ label: qsTr("↘"), dx: 1, dy: -1 })
            ]
            delegate: Rectangle {
              width: 72; height: 48; radius: 4
              color: (root.jogEnabled && ((modelData.dy > 0 && root.keyUpHeld) ||
                    (modelData.dy < 0 && root.keyDownHeld) ||
                    (modelData.dx > 0 && root.keyRightHeld) ||
                    (modelData.dx < 0 && root.keyLeftHeld))) ? Cores.CoreStyle.accent : Cores.CoreStyle.surface
              border.color: Cores.CoreStyle.border
              border.width: 1

              Text { anchors.centerIn: parent; text: modelData.label; color: Cores.CoreStyle.text }

              MouseArea {
                anchors.fill: parent
                enabled: root.jogEnabled && modelData.label.length > 0
                onClicked: {
                  if (modelData.dx !== 0)
                    jogX(modelData.dx, root.vFast)
                  if (modelData.dy !== 0)
                    jogY(modelData.dy, root.vFast)
                }
              }
            }
          }
        }
        Label {
          anchors.top: grid.bottom
          anchors.topMargin: 8
          anchors.horizontalCenter: grid.horizontalCenter
          text: qsTr("常规设置已禁用点动")
          color: "#f87171"
          visible: !root.jogEnabled && root.directControlEnabled
        }
      }

      ColumnLayout {
        spacing: 8
        Layout.alignment: Qt.AlignTop
        Item { Layout.fillHeight: true; width: 1 }
        Btns.ActionButton { text: qsTr("回零"); enabled: root.directControlEnabled; onClicked: Cores.CoreControl.home() }
        Btns.ActionButton { text: qsTr("设原点"); enabled: root.directControlEnabled; onClicked: Cores.CoreControl.setWorkOrigin() }
        Btns.ActionButton { text: qsTr("复位"); onClicked: Cores.CoreControl.reset() }
      }
    }
  }

  Item {
    anchors.fill: parent
    visible: !root.directControlEnabled
    Rectangle {
      anchors.fill: parent
      color: "#0f172a"
      opacity: 0.85
      radius: 8
    }
    Label {
      anchors.centerIn: parent
      text: qsTr("常规设置已禁用设备控制")
      color: "#94a3b8"
      font.pixelSize: 16
    }
  }
}
