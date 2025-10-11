import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
Item{
    property real padding: 20
    property string source: ""
    id:root
    Item{
        width: parent.width*0.95
        height: parent.height*0.95
    ColumnLayout{
        anchors.fill: parent
        spacing: 0
        Item{
            Layout.fillWidth: true
            Layout.fillHeight: true
        Item{
            anchors.centerIn: parent
            width: parent.width-padding*2
            height: width
            ItemIcon{

                Behavior on scale {NumberAnimation{ easing.type: Easing.OutBack;duration: 300}}
                width: parent.width
                height: width
                fillMode: Image.PreserveAspectFit
                source:root.source
                sourceSize: Qt.size(400,400)
            }
        }
        }
    }
    }
}
