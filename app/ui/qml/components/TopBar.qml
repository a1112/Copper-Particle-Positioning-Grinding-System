import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
  id: root
  signal startClicked()
  signal stopClicked()
  signal openSettings()
  signal openTestImages()

  spacing: 8
  Layout.fillWidth: true

  Button { text: "开始"; onClicked: root.startClicked() }
  Button { text: "停止"; onClicked: root.stopClicked() }
  Button { text: "设置"; onClicked: root.openSettings() }
  Button { text: "测试图片"; onClicked: root.openTestImages() }
}

