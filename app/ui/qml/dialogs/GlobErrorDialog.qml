import QtQuick
import QtCore
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Window
import "../cores" as Cores

Dialog {
  id: errorDialog
  title: "请求失败"
  parent: Overlay.overlay
  anchors.centerIn: parent
  width: 480
  modal: true
  standardButtons: Dialog.Ok
  visible: Cores.CoreError.globErrorVisible
  contentItem: Text { text: Cores.CoreError.globErrorText; wrapMode: Text.WordWrap; color: "white"; width: 420 }
  background: Rectangle { color: "#5b0000"; radius: 10 }

  onAccepted: Cores.CoreError.globErrorVisible = false
  onRejected: Cores.CoreError.globErrorVisible = false
}


