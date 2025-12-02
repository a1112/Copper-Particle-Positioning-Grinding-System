import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../"

RowLayout {
   property string groupId: groupBox.groupId

  Label {
    Layout.fillWidth: true
    text: ((modelData && modelData.label) || (modelData && modelData.id) || "" )+" "
    color: _labelColor(groupBox.groupId, modelData.id, modelData.default, "#e5e7eb")
    Layout.alignment: Qt.AlignVCenter
  }
  TextFieldBase {
    id: input
    dirty: _isFieldDirty(groupBox.groupId, modelData.id, modelData.default)
    text: String(_currentValue({ groupId: groupBox.groupId, id: modelData.id, default: modelData.default }))
    onEditingFinished: _updateValue(groupBox.groupId, modelData.id, text)
  }
  Item{
    width: 10
    height: 1
  }
}

