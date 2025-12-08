import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components/Base"
import "../../components/btns" as Btns
GroupBox {
  id: root

  title: qsTr("点位数据")
  property int tf_implicitHeight: 32
  property var pointsModel
  property int selectedIndex: -1
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
        clip: true
        anchors.fill: parent
        model: root.pointsModel ? root.pointsModel : []
        currentIndex: root.selectedIndex
        onCurrentIndexChanged: root.selectedIndex = currentIndex

        delegate: PintItem {
        }
      }
    }

      Connections {
        target: root
        function onMatricesChanged() {
          try {
            var cam = (root.matrices && root.matrices.camera_to_machine) ? root.matrices.camera_to_machine : []
            matricesText = JSON.stringify(cam)
          } catch(e) {
            matricesText = ""
          }
        }
      }

      RowLayout {
      Layout.fillWidth: true

        anchors.margins: 0
        spacing: 6
        Label {
          text: qsTr("相机->机床")
          color: "#cbd5e1"
          Layout.preferredWidth: 100
        }
        TextFieldBase {
          Layout.fillWidth: true
          readOnly: true
          implicitHeight: 35
          text: root.matricesText
        }
      }

  }
}
