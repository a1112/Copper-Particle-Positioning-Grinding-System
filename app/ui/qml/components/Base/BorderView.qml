import QtQuick
import QtQuick.Controls.Material
import QtQuick.Controls
Item{
anchors.fill: parent
    id:root
    property color bord_color:"red"// Dcolor.randColor()
    property real item_width: 2
    property bool runing: false
    property real duration: 300
    property real length_scale: 1.0
    Rectangle{
        anchors.top: parent.top
        height: item_width
        color: bord_color
        width: runing?parent.width*length_scale:0
        Behavior on width {SmoothedAnimation{duration: root.duration}}
        anchors.horizontalCenter: parent.horizontalCenter
    }
    Rectangle{
        color: bord_color
        anchors.bottom: parent.bottom
        height: item_width
        width: runing?parent.width*length_scale:0
        Behavior on width {SmoothedAnimation{duration: root.duration}}
        anchors.horizontalCenter: parent.horizontalCenter
    }
    Rectangle{
        color: bord_color
        anchors.left: parent.left
        width: item_width
        height:runing?root.height*length_scale:0
        Behavior on height {SmoothedAnimation{duration: root.duration}}
        anchors.verticalCenter: parent.verticalCenter
    }
    Rectangle{
        color: bord_color
        anchors.right: root.right
        width: item_width
        height:runing?root.height*length_scale:0
        Behavior on height {SmoothedAnimation{duration: root.duration}}
        anchors.verticalCenter: parent.verticalCenter
    }
}



