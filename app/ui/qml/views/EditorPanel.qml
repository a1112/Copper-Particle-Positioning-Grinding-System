import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
  id: root
  radius: 4
  color: "#1e1e1e"; border.color: "#333"

  ColumnLayout { anchors.fill: parent; anchors.margins: 8; spacing: 6
    RowLayout { Layout.fillWidth: true
      Label { text: "指令编辑"; font.bold: true; Layout.fillWidth: true }
      ComboBox {
        id: presetBox
        model: ["模板: 通用", "模板: G 代码示例", "模板: M 代码示例"]
        onCurrentIndexChanged: {
          if (currentIndex === 1 && editor.text.length === 0) {
            editor.text = "G0 X0 Y0 Z0\nG1 X10 Y10 F100\n";
          } else if (currentIndex === 2 && editor.text.length === 0) {
            editor.text = "M3 S1000\nG4 P1 ; dwell 1s\nM5\n";
          }
        }
      }
      Button { text: "运行" }
      Button { text: "停止" }
      Button { text: "打开" }
      Button { text: "保存" }
    }
    RowLayout {
      Layout.fillWidth: true
      Layout.fillHeight: true
      spacing: 0
      Rectangle {
        id: gutter
        color: "#202020"
        width: 48
        Layout.fillHeight: true
        Text {
          id: lineNums
          anchors.right: parent.right
          anchors.rightMargin: 6
          y: editor.contentItem ? (editor.contentItem.y + 4) : 4
          text: editor.text.length ? (function(){ var a = editor.text.split('\n'); var s = ''; for (var i=0;i<a.length;i++){ s += (i+1) + "\n"; } return s; })() : '1\n'
          color: "#888"
          font.family: "Consolas, 'Courier New', monospace"
          font.pixelSize: 14
          wrapMode: Text.NoWrap
          horizontalAlignment: Text.AlignRight
          verticalAlignment: Text.AlignTop
        }
      }
      TextArea {
        id: editor
        Layout.fillWidth: true
        Layout.fillHeight: true
        wrapMode: TextEdit.NoWrap
        font.family: "Consolas, 'Courier New', monospace"
        placeholderText: "在此编辑指令（支持 G/M 指令高亮）"
        onTextChanged: lineNums.text = (function(){ var a = editor.text.split('\n'); var s=''; for (var i=0;i<a.length;i++){ s += (i+1) + "\n"; } return s; })()
        Component.onCompleted: { if (pyHighlighter && editor.textDocument) pyHighlighter.attach(editor.textDocument) }
      }
    }
  }
}

