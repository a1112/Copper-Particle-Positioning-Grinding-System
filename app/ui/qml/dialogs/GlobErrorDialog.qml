import QtQuick
import QtCore
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Window
import "../cores" as Cores

Dialog {
  id: errorDialog
  title: qsTr("请求失败")
  parent: Overlay.overlay
  anchors.centerIn: parent
  width: 480
  modal: true
  standardButtons: Dialog.Ok
  visible: Cores.CoreError.globErrorVisible
  contentItem: TextArea {
    text: Cores.CoreError.globErrorText
    readOnly: true
    wrapMode: TextEdit.Wrap
    color: "white"
    selectByMouse: true
    selectByKeyboard: true
    background: null
    width: 420
  }
  background: Rectangle { color: "#5b0000"; radius: 10 }

  onAccepted: Cores.CoreError.globErrorVisible = false
  onRejected: Cores.CoreError.globErrorVisible = false
}
