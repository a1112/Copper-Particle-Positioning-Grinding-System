import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
ItemDelegate{
    property alias labelText: lab.text
    property alias labelColor: lab.color
    property alias labelRotation: lab.rotation
    property int labelPixelSize: width/1.5
    property alias labelScale: lab.scale
    ToolTip.visible: ToolTip.text&&hovered
    Label{
        id:lab
        scale:parent.hovered?2:1
        anchors.centerIn: parent
        font.pixelSize: labelPixelSize
        font.bold: true
        text: "▼"
        Behavior on rotation {NumberAnimation{duration: 400}}
        Behavior on scale {NumberAnimation{duration: 400}}
        Behavior on color {ColorAnimation{duration: 400}}
    }

}

