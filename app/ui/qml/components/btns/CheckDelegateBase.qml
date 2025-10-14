import QtQuick
import QtQuick.Controls
import "../../cores" as Cores

// 复选项委托（可控高度/自适应指示器）
CheckDelegate {
  id: control

  // 允许外部按需控制高度；未设置时使用默认 24
  property int controlHeight: 24
  implicitHeight: controlHeight
  spacing: 6
  padding: 6
  // 为内容预留左侧空间（指示器宽度 + 间距）避免文本覆盖勾选框
  leftPadding: (indicator ? indicator.width : 18) + 12

  // 基于实际高度自适应的指示器尺寸与对齐
  indicator: Rectangle {
    id: ind
    width: Math.round(Math.min(20, Math.max(14, control.height - 10)))
    height: width
    radius: 3
    anchors.left: parent.left
    anchors.leftMargin: 6
    anchors.verticalCenter: parent.verticalCenter
    color: control.checked ? Cores.CoreStyle.primary : Cores.CoreStyle.surface
    border.color: Cores.CoreStyle.border
    Text {
      anchors.centerIn: parent
      text: control.checked ? "✓" : ""
      color: control.checked ? "white" : "transparent"
      font.pixelSize: Math.round(parent.height * 0.8)
    }
  }

  // 文本垂直居中，适配可用高度
  contentItem: Text {
    text: control.text
    color: control.enabled ? Cores.CoreStyle.text : Cores.CoreStyle.muted
    verticalAlignment: Text.AlignVCenter
    horizontalAlignment: Text.AlignLeft
    elide: Text.ElideRight
    // 占满可用区域（已由 leftPadding 让出指示器空间）
    width: control.availableWidth
    height: control.availableHeight
  }
}
