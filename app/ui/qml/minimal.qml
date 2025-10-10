import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
  id: win
  visible: true
  width: 800
  height: 480
  title: "Copper UI (Fallback)"

  ColumnLayout {
    anchors.fill: parent
    spacing: 12
    Label { text: "已进入简化界面 (fallback)"; font.pixelSize: 18 }
    Label { text: "主界面 QML 加载失败或依赖未就绪" }
    Label { text: "请检查 PySide6/QML 模块（QtWebSockets/Controls/Layouts 等）"; wrapMode: Text.WordWrap }
    Button { text: "退出"; onClicked: Qt.quit() }
  }
}

