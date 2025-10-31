import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id:root
    signal requestCodeView()
    property var stageModel: []
    property var taskContext: null
    Layout.fillHeight: true
    Layout.fillWidth: true
    clip: true

    ScrollView{
        contentWidth: root.width
        contentHeight: root.enabled?col.height:0
        Behavior on contentHeight {NumberAnimation{duration: 900}}
        ColumnLayout{
            id:col
            x:4
            width: root.width-8
            spacing: 10
            anchors.margins: 4
            Repeater {
                model: stageModel
                delegate: TaskItem {
                    Layout.fillWidth: true
                    taskContext: root.taskContext
                    onRequestCodeView: root.requestCodeView()
                }
            }

        }
    }
}
