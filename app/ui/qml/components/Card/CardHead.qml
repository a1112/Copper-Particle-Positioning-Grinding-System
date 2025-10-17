import QtQuick
import QtQuick.Controls.Material
import"../../cores" as Cores
Item {
    width: parent.width
    height:Cores.CoreStyle.cardHeadHeight
    Pane{
        anchors.fill: parent
        Material.elevation: 6
    }

}
