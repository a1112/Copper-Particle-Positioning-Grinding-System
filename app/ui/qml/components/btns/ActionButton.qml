import QtQuick
import QtQuick.Controls
import "../../cores" as Cores

// 统一风格的操作按钮：圆角、分格风格、主题联动
Button {
  id: control
  // 可选危险态（如停止）
  property bool danger: false

  font.pixelSize: 13
  padding: 6

  background: Rectangle {
    radius: 4
    color: control.down
           ? (control.danger ? "#b91c1c" : Cores.CoreStyle.primary)
           : (control.hovered ? Cores.CoreStyle.surface : Cores.CoreStyle.background)
    border.color: Cores.CoreStyle.border
  }
  contentItem: Text {
    font.bold: true
    text: control.text
    color: control.down ? "white" : Cores.CoreStyle.text

  }
}

