import QtQuick
import QtQuick.Controls
import "../../cores" as Cores

// 统一风格的操作按钮：圆角、分格风格、主题联动
Button {
  id: control
  // 可选危险态（如停止）
  property bool danger: false
  // 外部可激活的高亮态（用于键盘反馈等）
  property bool active: false
  Rectangle{anchors.fill: parent;opacity:0.1}
  font.pixelSize: 13
  // 明确内边距与悬停行为，避免实际点击区域与视觉不一致
  padding: 3
  leftPadding: 6
  rightPadding: 6
  topPadding: 2
  bottomPadding: 2
  hoverEnabled: true

  // 基于内容计算隐式尺寸，减少布局产生的过大空白
  implicitWidth: Math.max(
                    64,
                    (contentItem ? contentItem.implicitWidth : 0)
                  )
  implicitHeight: Math.max(
                     28,
                     (contentItem ? contentItem.implicitHeight : 0)
                   )

  background: Rectangle {
    radius: 4
    anchors.fill: control
    color: (control.down || control.active)
           ? (control.danger ? "#b91c1c" : Cores.CoreStyle.primary)
           : Cores.CoreStyle.surface
    border.color: Cores.CoreStyle.border
  }
  contentItem: Text {
    font.bold: true
    text: control.text
    color: (control.down || control.active) ? "white" : Cores.CoreStyle.text
    horizontalAlignment: Text.AlignHCenter
    verticalAlignment: Text.AlignVCenter
    elide: Text.ElideRight
    width: control.availableWidth
    height: control.availableHeight

  }
}

