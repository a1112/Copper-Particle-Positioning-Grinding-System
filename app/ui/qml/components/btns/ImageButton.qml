import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material
ItemDelegate{
    property alias source: image.source
    property string tipText: ""
    ToolTip.visible: tipText!=="" && hovered
    ToolTip.text: tipText
    Item{
        anchors.fill: parent
        Image{
            id:image
            anchors.fill: parent
            fillMode: Image.PreserveAspectFit
        }
    }


}

