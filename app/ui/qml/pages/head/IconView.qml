import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../../cores" as Cores
Item{
    property real padding: 20
    property int icon_index: 0
    property string source:[Cores.CoreStyle.getIconSource("MZ.ico"), Cores.CoreStyle.getIconSource("MZ-old.ico")][icon_index]
    id:root
    ItemDelegate{
        anchors.fill: parent
        onClicked: {
            icon_index=(icon_index+1)%2
        }
    }

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

