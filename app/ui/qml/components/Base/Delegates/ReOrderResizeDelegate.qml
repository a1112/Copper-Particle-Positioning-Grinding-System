import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
ReOrderDelegate{
    /*

     */
    property Component reOrderItem
    property real seqWidth: 6//right
        dropItem:
            Item{
            width: load_item.width
            height: load_item.height
            Loader{
                id:load_item
                sourceComponent:reOrderItem
            }
            Item{
                id:seq_item
                height: parent.height
                width: seqWidth
                x:parent.width-width/2
                onXChanged: {
                    load_item.item.width=x+width/2
                }
                DragHandler{
                    id:dragH
                    yAxis.enabled: !orientation
                    xAxis.enabled: orientation
                }
                MouseArea{
                    acceptedButtons: Qt.NoButton
                    hoverEnabled: true
                    x:dragH.active?-1000:0
                    y:dragH.active?-1000:0
                    height: dragH.active?200:parent.height
                    width: dragH.active?2000:parent.width
                    cursorShape:containsMouse? Qt.SplitHCursor:Qt.ArrowCursor
                }
                MouseArea{
                    acceptedButtons: Qt.NoButton
                    hoverEnabled: true
                    x:dragH.active?-1000:0
                    y:dragH.active?-1000:0
                    height: dragH.active?2000:0
                    width: dragH.active?2000:0
                    cursorShape:containsMouse? Qt.SplitHCursor:Qt.ArrowCursor
                }
            }
        }

    }

