import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../Api" as Api
import "../../cores" as Cores
import "../Base"
import "../../components/btns" as Btns

// 简易云台式手动控制（方向 + 速度），支持键盘方向键
BaseCard {
  id: root

  // 快速/工作速度（mm/s）
  property int vFast: 100
  property int vWork: 10
  // 键盘按下状态用于按钮高亮反馈
  property bool keyUpHeld: false
  property bool keyDownHeld: false
  property bool keyLeftHeld: false
  property bool keyRightHeld: false

  Keys.priority: Keys.BeforeItem
  focus: true
  activeFocusOnTab: true

  function jogX(dir, spd){
    Api.ApiClient.jog('x', dir, spd, function(_){}, function(s,m){ console.log('jog x err', s, m) }) }

  function jogY(dir, spd){
    Api.ApiClient.jog('y', dir, spd, function(_){}, function(s,m){ console.log('jog y err', s, m) }) }

  // Shift 使用工作速度，其余使用快速速度
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
      Label { text: "Shift=工作速"; color: Cores.CoreStyle.muted }
    }

    RowLayout {
      Layout.fillWidth: true; spacing: 8
      Label { text: "快速(mm/s)"; color: Cores.CoreStyle.text }
      SpinBox { id: sbFast; from: 1; to: 1000; value: root.vFast; onValueModified: root.vFast = value; Layout.preferredWidth: 90 }
      Label { text: "工作(mm/s)"; color: Cores.CoreStyle.text }
      SpinBox { id: sbWork; from: 0; to: 200; value: root.vWork; onValueModified: root.vWork = value; Layout.preferredWidth: 90 }
      Btns.ActionButton { text: "设置速度"; onClicked: Api.ApiClient.setSpeed(root.vFast, root.vWork, function(_){}, function(s,m){ console.log('set_speed err', s, m) }) }
    }

    // 方向控制区：
    Item { Layout.fillWidth: true; Layout.fillHeight: true
      GridLayout { id: grid; columns: 3; rowSpacing: 8; columnSpacing: 8; anchors.centerIn: parent
        Btns.ActionButton { id: btnUL; text: "↖"; active: root.keyUpHeld && root.keyLeftHeld; onClicked: { jogX(-1, root.vFast); jogY(1, root.vFast) } }
        Btns.ActionButton { id: btnU;  text: "↑";  active: root.keyUpHeld && !root.keyLeftHeld && !root.keyRightHeld; onClicked: jogY(1, root.vFast) }
        Btns.ActionButton { id: btnUR; text: "↗"; active: root.keyUpHeld && root.keyRightHeld; onClicked: { jogX(1, root.vFast); jogY(1, root.vFast) } }
        Btns.ActionButton { id: btnL;  text: "←";  active: root.keyLeftHeld && !root.keyUpHeld && !root.keyDownHeld; onClicked: jogX(-1, root.vFast) }
        Rectangle { width: 1; height: 1; color: "transparent" }
        Btns.ActionButton { id: btnR;  text: "→";  active: root.keyRightHeld && !root.keyUpHeld && !root.keyDownHeld; onClicked: jogX(1, root.vFast) }
        Btns.ActionButton { id: btnDL; text: "↙"; active: root.keyDownHeld && root.keyLeftHeld; onClicked: { jogX(-1, root.vFast); jogY(-1, root.vFast) } }
        Btns.ActionButton { id: btnD;  text: "↓";  active: root.keyDownHeld && !root.keyLeftHeld && !root.keyRightHeld; onClicked: jogY(-1, root.vFast) }
        Btns.ActionButton { id: btnDR; text: "↘"; active: root.keyDownHeld && root.keyRightHeld; onClicked: { jogX(1, root.vFast); jogY(-1, root.vFast) } }
      }
    }
  }
}

