import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components/btns" as Btns

RowLayout {
  id: header
  property alias statusLabel: infoLabel
  Layout.fillWidth: true
  spacing: 12

  Label {
    text: qsTr("参数设置中心")
    font.bold: true
    font.pixelSize: 20
    color: "#f1f5f9"
  }

  Item { Layout.fillWidth: true }

  Label {
    id: infoLabel
    color: "#9AA5B1"
    text: ""
  }

  Btns.ActionButton {
    text: loading ? qsTr("刷新中…") : qsTr("刷新")
    enabled: !loading
    onClicked: refresh()
  }

  Btns.ActionButton {
    text: qsTr("导入")
    enabled: !loading
    onClicked: importCurrent()
  }

  Btns.ActionButton {
    text: qsTr("导出")
    enabled: !loading
    onClicked: exportCurrent()
  }

  Btns.ActionButton {
    text: qsTr("保存")
    enabled: !loading
    onClicked: saveCurrent()
  }

  Btns.ActionButton {
    text: qsTr("关闭")
    onClicked: root.close()
  }
}
