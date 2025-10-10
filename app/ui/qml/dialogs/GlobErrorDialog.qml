import QtQuick
import QtCore
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Window

Dialog {
  id: errorDialog
  title: "请求失败"
  parent: Overlay.overlay
  anchors.centerIn: parent
  width: 480
  modal: true
  standardButtons: Dialog.Ok
  visible: coreError.globErrorVisible
  contentItem: Text { text: coreError.globErrorText; wrapMode: Text.WordWrap; color: "white"; width: 420 }
  background: Rectangle { color: "#5b0000"; radius: 10 }

  onAccepted: coreError.globErrorVisible = false
  onRejected: coreError.globErrorVisible = false
}

