import QtQuick
import QtQuick.Controls.Material

import "../../../cores" as Cores

ItemDelegate {
        property bool selectd: Cores.CoreState.realViewIndex===index

        onClicked: {
                Cores.CoreState.realViewIndex=index
        }

        height:Cores.CoreStyle.cardHeadHeight
        Frame{
                anchors.fill: parent
        }
}
