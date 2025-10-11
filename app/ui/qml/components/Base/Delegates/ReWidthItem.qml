//  宽度调整
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
Item{
    id:root
    property real seqWidth: 6//right
    property Item target:parent
    property real minimumWidth: target.Layout.minimumWidth
    property real maximumWidth: target.Layout.maximumWidth
    property real p_width : target.width
    onP_widthChanged: {
        x=target.width-width/2
    }

    height: parent.height
    width: seqWidth
    x:target.width-width/2

    onXChanged: {
        target.width=x+width/2
    }
    DragHandler{
        id:dragH
        yAxis.enabled: false
        xAxis.enabled: true
        xAxis.minimum: minimumWidth
        xAxis.maximum: maximumWidth
    }
    MouseArea{
        enabled: root.enabled
        acceptedButtons: Qt.NoButton
        hoverEnabled: true
        x:dragH.active?-1000:0
        y:dragH.active?-1000:0
        height: dragH.active?200:parent.height
        width: dragH.active?2000:parent.width
        cursorShape:containsMouse? Qt.SplitHCursor:Qt.ArrowCursor
    }
    MouseArea{
        enabled: root.enabled
        acceptedButtons: Qt.NoButton
        hoverEnabled: true
        x:dragH.active?-1000:0
        y:dragH.active?-1000:0
        height: dragH.active?2000:0
        width: dragH.active?2000:0
        cursorShape:containsMouse? Qt.SplitHCursor:Qt.ArrowCursor
    }
}

