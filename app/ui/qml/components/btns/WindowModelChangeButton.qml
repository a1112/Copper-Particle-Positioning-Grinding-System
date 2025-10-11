import QtQuick
import "../../cores" as Cores`n    // 切换 全屏等
ColorItemDelegateButtonBase{
    tipText:qsTr("全屏/取消全屏")
    height: parent.height
    width: height
    property bool shouMaxIcon: true
    source: shouMaxIcon ? Cores.CoreStyle.getIconSource("FullScreen.png") : Cores.CoreStyle.getIconSource("WindowScreen.png")
}


