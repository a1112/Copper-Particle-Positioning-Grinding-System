import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components/Base"
import "../../cores" as Cores

EffectLabel {
  font.weight: Font.DemiBold
  font.pixelSize: 20
  font.letterSpacing: 1.2
  text: Cores.CoreUI.title
  color: Cores.CoreStyle.text
  opacity: 0.95
  Layout.alignment: Qt.AlignHCenter
}



