import QtQuick.Controls
import QtQuick.Layouts
import "../../components/Base"
import "../../cores" as Cores

EffectLabel {
  // 标题颜色，可按需覆盖，默认使用主题主色
  font.bold: true
  font.pointSize: 25
  text: Cores.Core.title
  color: Cores.CoreStyle.titleColor
  Layout.alignment: Qt.AlignHCenter
}


