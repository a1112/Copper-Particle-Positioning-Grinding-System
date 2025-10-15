import QtQuick
import QtQuick.Controls.Material
import QtQuick.Layouts
import "../../Sockets" as Sockets
import "../../Api" as Api
import "../Base"
import "../../cores" as Cores
import "../../components/btns" as Btns
Item {
    height:Cores.CoreStyle.cardHeadHeight
    Layout.fillWidth: true
    Pane{
        anchors.fill: parent
        Material.elevation: 5
    }
}
