import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../../cores" as Cores
import "../../datas" as Datas
import "../../works" as Works
import "../../Api" as Api
import "../../components/btns" as Btn
RowLayout {
  Layout.fillWidth: true
  height: 26
  spacing: 10
  Label {
    text: qsTr("指令状态与报警中心")
    font.pixelSize: 22
    font.bold: true
    color: Cores.CoreStyle.text
    Layout.alignment: Qt.AlignVCenter
  }
  Label {
    text: qsTr("流水号 %1 · %2").arg(statePageCore.currentSerial()).arg(statePageCore.readySummary())
    color: Cores.CoreStyle.muted
    elide: Text.ElideRight
    Layout.alignment: Qt.AlignVCenter
    Layout.fillWidth: true
  }
  Btn.ActionButton {
    text: statePageCore.refreshing ? qsTr("刷新中...") : qsTr("刷新")
    enabled: !statePageCore.refreshing
    Layout.alignment: Qt.AlignVCenter
    onClicked: statePageCore.refreshData()
  }
  Btn.ActionButton {
    text: qsTr("关闭")
    Layout.alignment: Qt.AlignVCenter
    onClicked: root.close()
  }
}
