import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../cores" as Cores

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
