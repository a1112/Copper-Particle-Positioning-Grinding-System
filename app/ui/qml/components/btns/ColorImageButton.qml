import QtQuick
import "../../cores" as Cores`nimport QtQuick.Layouts
import "../../cores" as Cores`nimport QtQuick.Controls
import "../../cores" as Cores`nimport QtQuick.Controls.Material
import "../../cores" as Cores`nimport QtGraphicalEffects
import "../Base"
Item{
    id:root
    height: parent.height
    width: height
    property bool selected: false
    property color selectColor: Material.color(Material.accent)
    property string tipText: ""
    ToolTip.visible: tipText!=="" && hovered
    ToolTip.text: tipText
    property alias source: efi.source
    Item{
        height: parent.height*0.9
        width: height
        anchors.centerIn: parent
        Image{
            visible: false
            id:efi
            height: parent.height
            width: height
            fillMode: Image.PreserveAspectFit
        }
        ColorOverlay {
            width: efi.width
            height: efi.height
            anchors.centerIn: parent
                source: efi
                color: root.selected?root.selectColor:
                                     Cores.CoreStyle.isDark?"#eee":"#2e2e2e"
                layer.enabled: true
                layer.effect:DropShadowBase{}
        }
    }
}


