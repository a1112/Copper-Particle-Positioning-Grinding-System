import QtQuick
import QtQuick.Controls

Item {
  id: root
  // api can be injected if needed later
  property var api
  property alias host: hostField.text
  property alias port: portField.text
  Column {
    spacing: 6
    Row { spacing: 6
      Label { text: "主机" }
      TextField { id: hostField; placeholderText: "127.0.0.1"; width: 150 }
      Label { text: "端口" }
      TextField { id: portField; placeholderText: "5000"; width: 80 }
      Button { text: (backend.commConnected ? "断开" : "连接"); onClicked: backend.toggleComm(hostField.text, parseInt(portField.text)) }
      Label { text: (backend.commConnected ? "已连接" : "未连接") }
    }
    TextArea { readOnly: true; text: backend.commLog; width: 400; height: 120 }
  }
}

