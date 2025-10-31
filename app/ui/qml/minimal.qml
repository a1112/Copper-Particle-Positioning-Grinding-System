import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
  id: win
  visible: true
  width: 800
  height: 480
  title: qsTr("Copper UI (Fallback)")

  ColumnLayout {
    anchors.fill: parent
    spacing: 12
    Label { text: qsTr("已进入简化界面 (fallback)"); font.pixelSize: 18 }
    Label { text: qsTr("主界面 QML 加载失败或依赖未就绪") }
    Label { text: qsTr("请检查 PySide6/QML 模块（QtWebSockets/Controls/Layouts 等）"); wrapMode: Text.WordWrap }
    Button { text: qsTr("退出"); onClicked: Qt.quit() }
  }
}


