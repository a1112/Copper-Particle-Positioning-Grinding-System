import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../cores" as Cores
import "../../components/Base"
import "../../components/btns"

Rectangle {
  id: estopBtn
  Layout.alignment: Qt.AlignVCenter
  height: Math.max(36, parent.height*0.8)
  width: height * 2.4
  radius: 8
  color: root.isRunning ? Cores.CoreStyle.danger : Cores.CoreStyle.muted
  border.color: root.isRunning ? "#b91c1c" : Cores.CoreStyle.border
  border.width: 1
  opacity: root.isRunning ? 1.0 : 0.5
  RowLayout { anchors.fill: parent; anchors.margins: 6; spacing: 6
    Image { source: Cores.CoreStyle.getIconSource("close.png"); fillMode: Image.PreserveAspectFit; Layout.preferredWidth: estopBtn.height*0.6; Layout.preferredHeight: estopBtn.height*0.6 }
    Label { text: "急停"; color: "white"; font.bold: true }
  }
  MouseArea { anchors.fill: parent; enabled: root.isRunning; onClicked: estopDialog.open() }
}
