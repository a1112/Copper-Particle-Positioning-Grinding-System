import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components/Base"
import "../../components/btns" as Btns

Rectangle {
  // 在列表中的索引
  required property int index
  // 外部传入的标定明细引用（detail）
  required property var item // 使用 required property var 声明变了存在 即可

  required property var detailRef
  // 由 ListModel 的 item 角色提供的点数据
  property var point: item
  // 文本框高度由外部面板传入
  property int tf_implicitHeight: 32

  width: parent ? parent.width : 0
  height: col.height + 5
  color: ListView.isCurrentItem ? "#020617" : "transparent"
  border.color: "#1e293b"
  border.width: ListView.isCurrentItem ? 1 : 0
  onFocusChanged: {
    if (focus){
        list.currentIndex = index
    }
  }
  MouseArea {
    anchors.fill: parent
    hoverEnabled: true
    onClicked: {
        list.currentIndex = index
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

  function _writeBack() {
    if (!detailRef || !detailRef.points)
      return
    var pts = detailRef.points
    if (index < 0 || index >= pts.length)
      return
    pts[index] = point
    detailRef.points = pts
    list.currentIndex = index
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
        field.onTextChanged: {
          _ensurePixel()
          point.pixel.x = _num(field.text)
          _writeBack()
        }
      }

      PointField {
        labelText: "Y"
        field.implicitHeight: tf_implicitHeight
        field.text: point && point.pixel ? point.pixel.y : ""
        field.onTextChanged: {
          _ensurePixel()
          point.pixel.y = _num(field.text)
          _writeBack()
        }
      }

      PointField {
        labelText: qsTr("CamX")
        field.implicitHeight: tf_implicitHeight
        field.width: 50
        field.text: point && point.camera ? point.camera.x : ""
        field.onTextChanged: {
          _ensureCamera()
          point.camera.x = _num(field.text)
          _writeBack()
        }
      }

      PointField {
        labelText: "Y"
        field.implicitHeight: tf_implicitHeight
        field.width: 50
        field.text: point && point.camera ? point.camera.y : ""
        field.onTextChanged: {
          _ensureCamera()
          point.camera.y = _num(field.text)
          _writeBack()
        }
      }

      PointField {
        labelText: "Z"
        field.implicitHeight: tf_implicitHeight
        field.width: 50
        field.text: point && point.camera ? point.camera.z : ""
        field.onTextChanged: {
          _ensureCamera()
          point.camera.z = _num(field.text)
          _writeBack()
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
        field.onTextChanged: {
          _ensureMachine()
          point.machine.x = _num(field.text)
          _writeBack()
        }
      }

      PointField {
        labelText: "Y"
        field.implicitHeight: tf_implicitHeight
        field.width: 50
        field.text: point && point.machine ? point.machine.y : ""
        field.onTextChanged: {
          _ensureMachine()
          point.machine.y = _num(field.text)
          _writeBack()
        }
      }

      PointField {
        labelText: "Z"
        field.implicitHeight: tf_implicitHeight
        field.width: 50
        field.text: point && point.machine ? point.machine.z : ""
        field.onTextChanged: {
          _ensureMachine()
          point.machine.z = _num(field.text)
          _writeBack()
        }
      }
    }
  }
}
