import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../"
Rectangle{
    property string groupId: groupBox.groupId
  height: 35
  Frame{
    anchors.fill: parent
  }
RowLayout {
  anchors.fill: parent
  Label {
    Layout.fillWidth: true
    text: ((modelData && modelData.label) || (modelData && modelData.id) || "" )+" "
    color: "#e5e7eb"
    Layout.alignment: Qt.AlignVCenter
    anchors.verticalCenter: parent.verticalCenter
  }
  TextFieldBase {
    id: input
    text: String(root._currentValue({ groupId: groupBox.groupId, id: modelData.id, default: modelData.default }))
    onEditingFinished: root._updateValue(groupBox.groupId, modelData.id, text)
  }
  Item{
    width: 10
    height: 1
  }
}
}
