import QtQuick
import "../../cores" as Cores`nimport QtQuick.Layouts
import "../../cores" as Cores`nimport QtQuick.Controls
import "../../cores" as Cores`nimport QtQuick.Controls.Material
import "../../cores" as Cores`nImageButton{
    source: Cores.CoreStyle.getIconSource("flush.png") // replaced getStyleIcon
    Item{
        anchors.fill: parent
        Image{
            id:image
            anchors.fill: parent
            fillMode: Image.PreserveAspectFit
        }
    }


}


