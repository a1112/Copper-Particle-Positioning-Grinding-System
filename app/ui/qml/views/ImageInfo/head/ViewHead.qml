import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


import "../../Base"
import "../../../cores" as Cores
import "../../../components/Base" as Base

BaseHead {

    RowLayout{
        anchors.fill: parent

        Base.ComboBoxBase{
            model: Cores.CoreUI.allImageType
            visible: Cores.CoreState.realViewName=="2D"
            onCurrentIndexChanged: Cores.CoreState.current2DShowIndex = currentIndex
        }
        MaskSelect{
            visible: Cores.CoreState.realViewName=="2D"
        }
        Item { Layout.fillWidth: true }
        Label { text: "视图"; color: Cores.CoreStyle.text; font.pixelSize: 14 }
        Item { Layout.fillWidth: true }
        ViewChiose{
        }
    }
}
