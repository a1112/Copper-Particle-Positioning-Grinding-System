import QtQuick
import QtQuick.Controls
import "../../cores" as Cores
ItemDelegate {
    implicitHeight: Cores.CoreStyle.cardHeadHeight
    height:Cores.CoreStyle.cardHeadHeight
    property string tipText: ""
    ToolTip.visible: tipText!=="" && hovered
    ToolTip.text: tipText
    Frame{
        enabled: false
            anchors.fill: parent
    }
}

