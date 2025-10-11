import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

BaseImage{
    id:root
    layer.enabled: true
    property bool effect: true
    property real horizontalOffset: 5
    property real verticalOffset: 5
    fillMode: Image.PreserveAspectFit
    layer.effect: DropShadowBase{
        id:drapShadow
        horizontalOffset:root.horizontalOffset
        verticalOffset:root.verticalOffset
        visible: effect
    }
    Behavior on scale {SmoothedAnimation{duration: 300}}
}
