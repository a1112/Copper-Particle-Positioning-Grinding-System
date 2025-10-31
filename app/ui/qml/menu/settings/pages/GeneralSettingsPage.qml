import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
  id: page
  property var data: ({})

  function collectPayload() {
    return data || {}
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 16
    spacing: 12
    Label {
      text: qsTr("常规参数设置")
      font.pixelSize: 18
      font.bold: true
      color: "#f8fafc"
    }
    Label {
      text: qsTr("暂无可配置项。未来的常规参数将在此展示。")
      color: "#94a3b8"
      wrapMode: Text.Wrap
    }
    Item { Layout.fillHeight: true }
  }
}
