import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id:root
    Layout.fillHeight: true
    Layout.fillWidth: true
    clip: true
    Frame{
        anchors.fill: parent
    }

    ScrollView{
        contentWidth: root.width
        contentHeight: col.height
        ColumnLayout{
            id:col
            width: root.width-10
            spacing: 10
            anchors.margins: 5
            Repeater {
                model: stageModel
                delegate:
                    TaskItem{
                      Layout.fillWidth: true
                }


            }

        }
    }
}
