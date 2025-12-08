import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components/Base"
import "../../components/btns" as Btns
import "."

Rectangle {
  required property int index
    required property var modelData
  property var point:modelData

  width: list.width
  height: col.height + 5
  color: ListView.isCurrentItem ? "#020617" : "transparent"
  border.color: "#1e293b"
  border.width: ListView.isCurrentItem ? 1 : 0

  MouseArea {
    anchors.fill: parent
    hoverEnabled: true
    onClicked: {
      list.currentIndex = index
      root.selectRequested(index)
    }
  }

  function _num(text) {
    var n = Number(String(text).trim())
    return isNaN(n) ? null : n
  }

  function _ensurePixel() {
    if (!point.pixel)
      point.pixel = { x: null, y: null }
  }
  function _ensureCamera() {
    if (!point.camera)
      point.camera = { x: null, y: null, z: null }
  }
  function _ensureMachine() {
    if (!point.machine)
      point.machine = { x: null, y: null, z: null }
  }

  ColumnLayout {
    id: col
    width: parent.width
    anchors.margins: 4
    spacing: 2

    RowLayout {
      Layout.fillWidth: true
      spacing: 4
      Label {
        text: index + 1
        color: ListView.isCurrentItem ? "#0b1220" : "#e5e7eb"
        width: 15
      }

      PointField {
        labelText: qsTr("Px")
        field.implicitHeight: tf_implicitHeight
        field.text: point && point.pixel ? point.pixel.x : ""
        field.onEditingFinished: {
          _ensurePixel()
          point.pixel.x = _num(field.text)
        }
      }

      PointField {
        labelText: "Y"
        field.implicitHeight: tf_implicitHeight
        field.text: point && point.pixel ? point.pixel.y : ""
        field.onEditingFinished: {
          _ensurePixel()
          point.pixel.y = _num(field.text)
        }
      }

      PointField {
        labelText: qsTr("CamX")
        field.implicitHeight: tf_implicitHeight
        field.width: 50
        field.text: point && point.camera ? point.camera.x : ""
        field.onEditingFinished: {
          _ensureCamera()
          point.camera.x = _num(field.text)
        }
      }

      PointField {
        labelText: "Y"
        field.implicitHeight: tf_implicitHeight
        field.width: 50
        field.text: point && point.camera ? point.camera.y : ""
        field.onEditingFinished: {
          _ensureCamera()
          point.camera.y = _num(field.text)
        }
      }

      PointField {
        labelText: "Z"
        field.implicitHeight: tf_implicitHeight
        field.width: 50
        field.text: point && point.camera ? point.camera.z : ""
        field.onEditingFinished: {
          _ensureCamera()
          point.camera.z = _num(field.text)
        }
      }
    }

    RowLayout {
      Layout.fillWidth: true
      spacing: 4
      Item { width: 20 }

      PointField {
        labelText: qsTr("MachX")
        field.implicitHeight: tf_implicitHeight
        field.width: 50
        field.text: point && point.machine ? point.machine.x : ""
        field.onEditingFinished: {
          _ensureMachine()
          point.machine.x = _num(field.text)
        }
      }

      PointField {
        labelText: "Y"
        field.implicitHeight: tf_implicitHeight
        field.width: 50
        field.text: point && point.machine ? point.machine.y : ""
        field.onEditingFinished: {
          _ensureMachine()
          point.machine.y = _num(field.text)
        }
      }

      PointField {
        labelText: "Z"
        field.implicitHeight: tf_implicitHeight
        field.width: 50
        field.text: point && point.machine ? point.machine.z : ""
        field.onEditingFinished: {
          _ensureMachine()
          point.machine.z = _num(field.text)
        }
      }
    }
  }
}
