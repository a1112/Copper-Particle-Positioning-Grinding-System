import QtQuick
import QtQuick.Controls
import "../../components/Base"
import "../../cores" as Cores
// Company label only (no core dependency)
EffectLabel{
  id: root
  font.bold: true
  font.pointSize: 20
  text: Cores.CoreUI.companyName
  horizontalAlignment: Text.AlignHCenter
  verticalAlignment: Text.AlignVCenter
  elide: Text.ElideRight
}

