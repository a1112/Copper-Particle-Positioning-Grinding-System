import QtQuick
import QtQuick.Controls.Material

import QtQuick.Layouts
import "../../components/Base"
EffectImage {
    id: name
    height: parent.height
    width: height
    fillMode: Image.PreserveAspectFit
    sourceSize: Qt.size(height,width)
    horizontalOffset: 8
    verticalOffset: 8
}
