import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components/Base"
import "../../components/btns" as Btns
GroupBox {
  id: root
  title: qsTr("点位数据")

  property ListModel pointsModel: null
  property int selectedIndex: -1
  property var editor: ({})
  property var matrices: ({})
  property string matricesText: ""

  signal selectRequested(int index)
  signal addRequested()
  signal updateRequested()
  signal deleteRequested()
  signal matricesUpdated(var matrices)

  Component.onCompleted: {
    try {
      matricesText = JSON.stringify(root.matrices || {}, null, 2)
    } catch(e) {
      matricesText = ""
    }
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 8
    spacing: 6
    RowLayout {
      Layout.fillWidth: true
      spacing: 8
      Btns.ActionButton {
        text: qsTr("添加")
        onClicked: {
            root.addRequested()
      }
      }
      Btns.ActionButton {
        text: qsTr("删除当前")
        enabled: root.selectedIndex >= 0
        onClicked: root.deleteRequested()
      }
      Item { Layout.fillWidth: true }
      Label {
        text: qsTr("点击列表行即可选中并在上方编辑")
        color: "#94a3b8"
      }
    }

    Rectangle {
      Layout.fillWidth: true
      Layout.fillHeight: true
      color: "#00000015"
      radius: 4
      border.color: "#1e293b"

      ListView {
        id: list
        anchors.fill: parent
        model: root.pointsModel ? root.pointsModel : []
        currentIndex: root.selectedIndex
        onCurrentIndexChanged: root.selectedIndex = currentIndex
        delegate: RowLayout {
          required property int index
          property var point: (model.item !== undefined)
                               ? model.item
                               : (modelData.item !== undefined ? modelData.item : modelData)
          Layout.fillWidth: true
          spacing: 6

          MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            onClicked: {
              list.currentIndex = index
              root.selectRequested(index)
            }
          }

          Label {
            text: index + 1
            color: ListView.isCurrentItem ? "#0b1220" : "#e5e7eb"
            width: 20
          }

          Label { text: qsTr("Px"); color: "#cbd5e1" }
          TextFieldBase {
            width: 50
            text: ListView.isCurrentItem
                  ? (editor.pixelX !== undefined ? editor.pixelX : "")
                  : (point && point.pixel ? point.pixel.x : "")
            onTextChanged: {
              if (ListView.isCurrentItem)
                editor.pixelX = text
            }
            onActiveFocusChanged: {
              if (activeFocus && !ListView.isCurrentItem) {
                list.currentIndex = index
                root.selectRequested(index)
              }
            }
          }
          Label { text: "Y"; color: "#cbd5e1" }
          TextFieldBase {
            width: 50
            text: ListView.isCurrentItem
                  ? (editor.pixelY !== undefined ? editor.pixelY : "")
                  : (point && point.pixel ? point.pixel.y : "")
            onTextChanged: {
              if (ListView.isCurrentItem)
                editor.pixelY = text
            }
            onActiveFocusChanged: {
              if (activeFocus && !ListView.isCurrentItem) {
                list.currentIndex = index
                root.selectRequested(index)
              }
            }
          }

          Label { text: qsTr("CamX"); color: "#cbd5e1" }
          TextFieldBase {
            width: 50
            text: ListView.isCurrentItem
                  ? (editor.cameraX !== undefined ? editor.cameraX : "")
                  : (point && point.camera ? point.camera.x : "")
            onTextChanged: {
              if (ListView.isCurrentItem)
                editor.cameraX = text
            }
            onActiveFocusChanged: {
              if (activeFocus && !ListView.isCurrentItem) {
                list.currentIndex = index
                root.selectRequested(index)
              }
            }
          }
          Label { text: "Y"; color: "#cbd5e1" }
          TextFieldBase {
            width: 50
            text: ListView.isCurrentItem
                  ? (editor.cameraY !== undefined ? editor.cameraY : "")
                  : (point && point.camera ? point.camera.y : "")
            onTextChanged: {
              if (ListView.isCurrentItem)
                editor.cameraY = text
            }
            onActiveFocusChanged: {
              if (activeFocus && !ListView.isCurrentItem) {
                list.currentIndex = index
                root.selectRequested(index)
              }
            }
          }
          Label { text: "Z"; color: "#cbd5e1" }
          TextFieldBase {
            width: 50
            text: ListView.isCurrentItem
                  ? (editor.cameraZ !== undefined ? editor.cameraZ : "")
                  : (point && point.camera ? point.camera.z : "")
            onTextChanged: {
              if (ListView.isCurrentItem)
                editor.cameraZ = text
            }
            onActiveFocusChanged: {
              if (activeFocus && !ListView.isCurrentItem) {
                list.currentIndex = index
                root.selectRequested(index)
              }
            }
          }

          Label { text: qsTr("MachX"); color: "#cbd5e1" }
          TextFieldBase {
            width: 50
            text: ListView.isCurrentItem
                  ? (editor.machineX !== undefined ? editor.machineX : "")
                  : (point && point.machine ? point.machine.x : "")
            onTextChanged: {
              if (ListView.isCurrentItem)
                editor.machineX = text
            }
            onActiveFocusChanged: {
              if (activeFocus && !ListView.isCurrentItem) {
                list.currentIndex = index
                root.selectRequested(index)
              }
            }
          }
          Label { text: "Y"; color: "#cbd5e1" }
          TextFieldBase {
            width: 50
            text: ListView.isCurrentItem
                  ? (editor.machineY !== undefined ? editor.machineY : "")
                  : (point && point.machine ? point.machine.y : "")
            onTextChanged: {
              if (ListView.isCurrentItem)
                editor.machineY = text
            }
            onActiveFocusChanged: {
              if (activeFocus && !ListView.isCurrentItem) {
                list.currentIndex = index
                root.selectRequested(index)
              }
            }
          }
          Label { text: "Z"; color: "#cbd5e1" }
          TextFieldBase {
            width: 50
            text: ListView.isCurrentItem
                  ? (editor.machineZ !== undefined ? editor.machineZ : "")
                  : (point && point.machine ? point.machine.z : "")
            onTextChanged: {
              if (ListView.isCurrentItem)
                editor.machineZ = text
            }
            onActiveFocusChanged: {
              if (activeFocus && !ListView.isCurrentItem) {
                list.currentIndex = index
                root.selectRequested(index)
              }
            }
          }
        }
      }
    }

    GroupBox {
      title: qsTr("矩阵(JSON)")
      Layout.fillWidth: true
      Layout.preferredHeight: 120

      Connections {
        target: root
        function onMatricesChanged() {
          try {
            matricesText = JSON.stringify(root.matrices || {}, null, 2)
          } catch(e) {
            matricesText = ""
          }
        }
      }

      Flickable {
        anchors.fill: parent
        contentWidth: parent.width
        contentHeight: matrixField.implicitHeight
        clip: true

        TextArea {
          id: matrixField
          text: root.matricesText
          wrapMode: TextArea.NoWrap
          selectByMouse: true
          onTextChanged: {
            root.matricesText = text
            try {
              var parsed = JSON.parse(text)
              root.matricesUpdated(parsed)
            } catch(e) {
            }
          }
          readOnly: false
          font.family: "Consolas"
          Layout.fillWidth: true
          Layout.fillHeight: true
        }
      }
    }
  }
}
