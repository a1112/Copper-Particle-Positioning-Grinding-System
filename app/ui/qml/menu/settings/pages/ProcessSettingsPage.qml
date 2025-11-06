import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
  id: page
  anchors.fill: parent
  property var data: ({})

  function collectPayload() {
    return data || {}
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 16
    spacing: 12
    Label {
      text: qsTr("工艺参数设置")
      font.pixelSize: 18
      font.bold: true
      color: "#f8fafc"
    }
    Label {
      anchors.centerIn: parent
      font.bold: true
      font.pixelSize: 20
      text: qsTr("暂未开放工艺参数配置。")
      wrapMode: Text.Wrap
    }
    Item { Layout.fillHeight: true }
  }
}
