import QtQuick
import QtQuick.Controls
Rectangle{
    layer.effect: DropShadowBase{
        horizontalOffset: 5
        verticalOffset: 5
        radius: 8.0
        samples: 17
        color: "#52000000"
    }
    layer.enabled: true
}

