import QtQuick
import "../../cores" as Cores`nimport QtQuick.Controls
import "../../cores" as Cores`nimport "../Labels"
import "../Base"
 BtnBase{
        EffectLabel{
            text: qsTr("下一卷")
        }
        ColorImageButton {
            id: name
            height: parent.height
            width: height
            source: Cores.CoreStyle.getIconSource("arrow-next.png")
            scale: hovered && cliac_enabled ?1.3:1
            Behavior on scale {
            NumberAnimation{
            duration: 300
            }
            }
        }
    }


