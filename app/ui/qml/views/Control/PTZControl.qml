import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../cores" as Cores
import "../Base"
import "../../components/btns" as Btns

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

  Keys.priority: Keys.BeforeItem
  focus: true
  activeFocusOnTab: true

  function jogX(dir, spd){ Cores.CoreControl.jog('x', dir, spd) }
  function jogY(dir, spd){ Cores.CoreControl.jog('y', dir, spd) }
  function keySpeed(ev){ return (ev.modifiers & Qt.ShiftModifier) ? vWork : vFast }

  Keys.onPressed: function(ev){
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
    anchors.margins: 8
    spacing: 8

    RowLayout {
      Layout.fillWidth: true
      Label { text: "云台控制"; color: Cores.CoreStyle.text; font.bold: true; Layout.fillWidth: true }
      Label { text: "Shift=工作速度"; color: Cores.CoreStyle.muted }
    }

    RowLayout {
      Layout.fillWidth: true; spacing: 8
      Label { text: "快速(mm/s)"; color: Cores.CoreStyle.text }
      SpinBox { id: sbFast; from: 1; to: 1000; value: root.vFast; onValueModified: root.vFast = value; Layout.preferredWidth: 90 }
      Label { text: "工作(mm/s)"; color: Cores.CoreStyle.text }
      SpinBox { id: sbWork; from: 0; to: 200; value: root.vWork; onValueModified: root.vWork = value; Layout.preferredWidth: 90 }
      Btns.ActionButton { text: "设置速度"; onClicked: Cores.CoreControl.setSpeed(root.vFast, root.vWork) }
    }

    // 控制区
    RowLayout {
      Layout.fillWidth: true; Layout.fillHeight: true; spacing: 16

      // 左侧：3x3 箭头矩形按钮
      Item { Layout.fillWidth: true; Layout.fillHeight: true
        GridLayout {
          id: grid; columns: 3; rowSpacing: 8; columnSpacing: 8; anchors.centerIn: parent
          Rectangle { width: 72; height: 48; radius: 4; color: (root.keyUpHeld && root.keyLeftHeld ? Cores.CoreStyle.accent : Cores.CoreStyle.surface); border.color: Cores.CoreStyle.border
            Text { anchors.centerIn: parent; text: "↖"; color: Cores.CoreStyle.text }
            MouseArea { anchors.fill: parent; onClicked: { jogX(-1, root.vFast); jogY(1, root.vFast) } }
          }
          Rectangle { width: 72; height: 48; radius: 4; color: (root.keyUpHeld && !root.keyLeftHeld && !root.keyRightHeld ? Cores.CoreStyle.accent : Cores.CoreStyle.surface); border.color: Cores.CoreStyle.border
            Text { anchors.centerIn: parent; text: "↑"; color: Cores.CoreStyle.text }
            MouseArea { anchors.fill: parent; onClicked: jogY(1, root.vFast) }
          }
          Rectangle { width: 72; height: 48; radius: 4; color: (root.keyUpHeld && root.keyRightHeld ? Cores.CoreStyle.accent : Cores.CoreStyle.surface); border.color: Cores.CoreStyle.border
            Text { anchors.centerIn: parent; text: "↗"; color: Cores.CoreStyle.text }
            MouseArea { anchors.fill: parent; onClicked: { jogX(1, root.vFast); jogY(1, root.vFast) } }
          }
          Rectangle { width: 72; height: 48; radius: 4; color: (root.keyLeftHeld && !root.keyUpHeld && !root.keyDownHeld ? Cores.CoreStyle.accent : Cores.CoreStyle.surface); border.color: Cores.CoreStyle.border
            Text { anchors.centerIn: parent; text: "←"; color: Cores.CoreStyle.text }
            MouseArea { anchors.fill: parent; onClicked: jogX(-1, root.vFast) }
          }
          Rectangle { width: 72; height: 48; color: "transparent" }
          Rectangle { width: 72; height: 48; radius: 4; color: (root.keyRightHeld && !root.keyUpHeld && !root.keyDownHeld ? Cores.CoreStyle.accent : Cores.CoreStyle.surface); border.color: Cores.CoreStyle.border
            Text { anchors.centerIn: parent; text: "→"; color: Cores.CoreStyle.text }
            MouseArea { anchors.fill: parent; onClicked: jogX(1, root.vFast) }
          }
          Rectangle { width: 72; height: 48; radius: 4; color: (root.keyDownHeld && root.keyLeftHeld ? Cores.CoreStyle.accent : Cores.CoreStyle.surface); border.color: Cores.CoreStyle.border
            Text { anchors.centerIn: parent; text: "↙"; color: Cores.CoreStyle.text }
            MouseArea { anchors.fill: parent; onClicked: { jogX(-1, root.vFast); jogY(-1, root.vFast) } }
          }
          Rectangle { width: 72; height: 48; radius: 4; color: (root.keyDownHeld && !root.keyLeftHeld && !root.keyRightHeld ? Cores.CoreStyle.accent : Cores.CoreStyle.surface); border.color: Cores.CoreStyle.border
            Text { anchors.centerIn: parent; text: "↓"; color: Cores.CoreStyle.text }
            MouseArea { anchors.fill: parent; onClicked: jogY(-1, root.vFast) }
          }
          Rectangle { width: 72; height: 48; radius: 4; color: (root.keyDownHeld && root.keyRightHeld ? Cores.CoreStyle.accent : Cores.CoreStyle.surface); border.color: Cores.CoreStyle.border
            Text { anchors.centerIn: parent; text: "↘"; color: Cores.CoreStyle.text }
            MouseArea { anchors.fill: parent; onClicked: { jogX(1, root.vFast); jogY(-1, root.vFast) } }
          }
        }
      }

      // 右侧：功能按钮
      ColumnLayout {
        spacing: 8
        Layout.alignment: Qt.AlignTop
        Btns.ActionButton { text: "回零"; onClicked: Cores.CoreControl.home() }
        Btns.ActionButton { text: "设原点"; onClicked: Cores.CoreControl.setWorkOrigin() }
        Btns.ActionButton { text: "复位"; onClicked: Cores.CoreControl.reset() }
      }
    }
  }
}
