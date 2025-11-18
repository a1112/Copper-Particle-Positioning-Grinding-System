import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
ScrollView{
  id:root
  Layout.fillWidth: true
  Layout.fillHeight: true
  implicitHeight: col.height
  implicitWidth: parent.width
ColumnLayout {
  id:col
  width: root.width
  spacing: 5

  Repeater {
    id: groupRepeater
    model:groupRepeaterModel
    delegate: GroupBox {
      id: groupBox
      Layout.fillWidth: true
      title: (modelData && modelData.label) || (modelData && modelData.id) || qsTr("未命名分组")
      property string groupId: modelData && modelData.id ? modelData.id : ""
      GridLayout {
        width: parent.width
        id: grid
        columns: 3
        rowSpacing: 2
        columnSpacing: 5
        Repeater {
          model: modelData && modelData.fields ? modelData.fields : []
            AutoSettingsPageShowItem{
              width:root.width/grid.columns
            }
        }
      }
    }
  }
}
}

