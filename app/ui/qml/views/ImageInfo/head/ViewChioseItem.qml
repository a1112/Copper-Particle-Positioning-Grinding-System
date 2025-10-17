import QtQuick
import QtQuick.Controls.Material

import "../../../cores" as Cores
import "../../../components/btns"
ItemDelegateBase {
        property bool selectd: Cores.CoreState.realViewIndex===index

        onClicked: {
                Cores.CoreState.realViewIndex=index
        }



}
