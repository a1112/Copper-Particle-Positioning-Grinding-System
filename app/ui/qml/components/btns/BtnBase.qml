import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
Row{
    spacing: 5
    id:row
    signal clicked()
    property alias cliac_enabled:  btb.enabled
    property alias hovered: btb.hovered
    Item{
        MouseArea{
            width: row.width
            height: row.height
            enabled: !cliac_enabled
            acceptedButtons: Qt.NoButton
            hoverEnabled: true
            cursorShape:!cliac_enabled?Qt.ForbiddenCursor:Qt.PointingHandCursor
        }
        ItemDelegate{
            id:btb
            width: row.width
            height: row.height
            onClicked: row.clicked()
        }
    }
}

