import QtQuick
import QtQuick.Controls
ItemDelegate {
    property string tipText: ""
    ToolTip.visible: tipText!=="" && hovered
    ToolTip.text: tipText
}

