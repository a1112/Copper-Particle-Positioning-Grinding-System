import QtQuick
import QtQuick.Controls
import "../Base"
ItemDelegateBase {
    height: parent.height
    width: height

    property alias selected: efi.selected
    property alias source: efi.source
    property alias selectColor: efi.selectColor
    MouseArea{
    anchors.fill: parent
    acceptedButtons: Qt.NoButton
    cursorShape: Qt.PointingHandCursor
    }
    Item{
        height: parent.height*0.66
        width: height
        anchors.centerIn: parent
        ColorImageButton{
            id:efi
            height: parent.height
            width: height
        }
    }
}

