import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components/btns" as Btns
import "../../components/Base"

Item {
  id: root
  height: col.implicitHeight

  property var groups: []
  property string activeName: ""

  signal createRequested(string name)
  signal activateRequested(string name)
  signal deleteRequested(string name)
  signal renameRequested(string oldName, string newName)
  signal openFolderRequested(string name)

  onActiveNameChanged: {
    if (activeName && activeName.length > 0)
      nameField.text = activeName
  }

  function _activeGroupFolder() {
    if (!groups || !activeName)
      return ""
    for (var i = 0; i < groups.length; ++i) {
      var g = groups[i]
      if (g && g.name === activeName)
        return g.folder || ""
    }
    return ""
  }

  ColumnLayout {
    id: col
    anchors.margins: 3
    spacing: 6
    width: parent.width

    RowLayout {
      Layout.fillWidth: true
      spacing: 6

      TextFieldBase {
        id: nameField
        Layout.fillWidth: true
        placeholderText: qsTr("分组名（可用于新增或重命名）")
      }

      Btns.ActionButton {
        text: qsTr("添加")
        onClicked: root.createRequested(nameField.text)
      }

      Btns.ActionButton {
        text: qsTr("修改")
        enabled: root.activeName.length > 0 && nameField.text.length > 0
        onClicked: root.renameRequested(root.activeName, nameField.text)
      }

      Btns.ActionButton {
        text: qsTr("打开保存位置")
        enabled: root.activeName.length > 0
        onClicked: {
          var folder = root._activeGroupFolder()
          if (folder && folder.length > 0)
            Qt.openUrlExternally("file:///" + folder.replace(/\\/g, "/"))
        }
      }
    }

    Rectangle {
      Layout.fillWidth: true
      Layout.preferredHeight: 160
      color: "#00000015"
      radius: 4
      border.color: "#1e293b"

      ListView {
        id: list
        anchors.fill: parent
        model: root.groups

        delegate: Rectangle {
          width: parent ? parent.width : 360
          height: 36
          color: (modelData.active || modelData.name === root.activeName) ? "#0ea5e9" : "transparent"
          border.width: 0

          RowLayout {
            anchors.fill: parent
            anchors.margins: 1
            spacing: 4

            Label {
              text: modelData.name
              color: (modelData.active || modelData.name === root.activeName) ? "#0b1220" : "#e5e7eb"
              font.bold: modelData.active || modelData.name === root.activeName
            }
            Label {
              text: qsTr("%1 点").arg(modelData.points_count || 0)
              color: "#cbd5e1"
            }
            Item { Layout.fillWidth: true }

            Btns.AddButton {
              text: qsTr("切换")
              enabled: modelData.name !== root.activeName
              onClicked: root.activateRequested(modelData.name)
            }
            Btns.AddButton {
              text: qsTr("删除")
              onClicked: root.deleteRequested(modelData.name)
            }
          }
        }
      }
    }
  }
}

