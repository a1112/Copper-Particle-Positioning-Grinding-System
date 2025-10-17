import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../cores" as Cores

Label {
  Layout.fillWidth: true
  Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
  color: Cores.CoreStyle.text
  elide: Text.ElideRight
  horizontalAlignment: Text.AlignHCenter
  verticalAlignment: Text.AlignVCenter
}
