import QtQuick
import "../../cores" as Cores`nimport QtQuick.Controls
import "../../cores" as Cores`nimport "../Labels"
import "../Base"
 BtnBase{
        ColorImageButton {
            id: name
//            fillMode: Image.PreserveAspectFit
            source: Cores.CoreStyle.getIconSource("arrow-pre.png")

        }
        EffectLabel{
            text: qsTr("上一卷")
        }
    }


