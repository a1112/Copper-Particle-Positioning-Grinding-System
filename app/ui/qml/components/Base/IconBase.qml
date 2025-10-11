import QtQuick
import QtQuick.Controls
Item{
    height: parent.height
    width: height
    id: root
    property string toolText:""
    ToolTip.text: toolText
    ToolTip.visible: toolText!=""&&hovered
    property alias hovered: itDe.hovered
    property alias source: icon.source
    signal clicked()
ItemDelegate{
    id:itDe
    anchors.fill: parent
    onClicked: root.clicked()
}
EffectImage{
    id:icon
    width: itDe.hovered? parent.width*0.9:parent.width*0.7
    Behavior on width {NumberAnimation{duration: 300}}
    height: width
    anchors.centerIn: parent
}
}

