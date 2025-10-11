//  宽度调整
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
Item{
    id:seq_item
        property real seqWidth: 6//right
    property Item target:parent
    property real
    minimumHeight: target.Layout.
    minimumHeight
    property real
    maximumHeight: target.Layout.
    maximumHeight
    height: seqWidth
    width: parent.width
    y:target.height-height/2

    onYChanged: {
        target.height=x+height/2
        y=target.height-height/2
    }
    DragHandler{
        id:dragH
        yAxis.enabled: true
        yAxis.minimum: minimumHeight
        yAxis.maximum: maximumHeight
        xAxis.enabled: false
    }
    MouseArea{
        acceptedButtons: Qt.NoButton
        hoverEnabled: true
        x:dragH.active?-1000:0
        y:dragH.active?-1000:0
        height: dragH.active?200:parent.height
        width: dragH.active?2000:parent.width
        cursorShape:containsMouse? Qt.SplitVCursor:Qt.ArrowCursor
    }
    MouseArea{
        acceptedButtons: Qt.NoButton
        hoverEnabled: true
        x:dragH.active?-1000:0
        y:dragH.active?-1000:0
        height: dragH.active?2000:0
        width: dragH.active?2000:0
        cursorShape:containsMouse? Qt.SplitVCursor:Qt.ArrowCursor
    }
}

