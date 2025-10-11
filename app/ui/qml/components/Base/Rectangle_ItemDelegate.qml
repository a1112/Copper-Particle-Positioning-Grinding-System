import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtGraphicalEffects
import QtQuick.Controls.impl
import QtQuick.Controls.Material
import QtQuick.Controls.Material.impl
import "../Label"
Rectangle{
    id:root
    height: 30
    radius: height/2
    width: maxWidth!=-1? lab.contentWidth+leftPadding+rightPadding:maxWidth
    property real rightPadding: 10
    property real leftPadding: 10
    property bool dragable : true//可拖拽？
    property string text: ""
    property alias _text_: lab.text
    property real maxWidth: 150
    property alias font: lab.font
    property alias fontColor: lab.color
    property bool checked: false
    property alias hovered:  mourse.containsMouse
    property alias containsMouse: mourse.containsMouse
    property alias lab_rotation: lab.rotation
    property alias label: textMetrics
    property bool effect: true // 外阴影
    property alias pressed_: mourse.pressed
    property alias hoverEnabled: mourse.hoverEnabled
    property bool enabled:true
    property alias acceptedButtons: mourse.acceptedButtons
    signal clicked(var mouse)
    signal click(var mouse)
    signal canceled()
    signal doubleClicked(var mouse)
    signal entered()
    signal exited()
    signal pressed(var mouse)
    signal released(var mouse)
    signal positionChanged(var mouse)
    Rectangle{
        color:!root.enabled?"transparent":mourse.containsMouse ? Material.listHighlightColor :"transparent"
        Behavior on color {ColorAnimation{duration: 400}}
        anchors.fill: parent
        radius: root.radius
        clip: true
        id:bg
        Ripple {
            clipRadius: root.radius
            id:rip
            width: parent.width
            height: parent.height
            clip: visible
            pressed: mourse.pressed|checked
            anchor: bg
            active:mourse.pressed|checked
            color: Material.rippleColor
        }
        TextMetrics{
            id: textMetrics
            font:lab.font
            elide: Text.ElideRight
            elideWidth: maxWidth-rightPadding-leftPadding
            text:root.text
        }
        BaseLabel{
            id:lab
            text: textMetrics.elidedText
            color: root.enabled ? root.Material.foreground : root.Material.hintTextColor
            anchors.horizontalCenterOffset: root.leftPadding-root.rightPadding
            anchors.centerIn: parent
            Behavior on color {
                ColorAnimation {
                    duration: 300
                }}
        }
        MouseArea{
            anchors.fill: parent
            hoverEnabled: enabled
            enabled: root.enabled
           onPressed:root.pressed(mouse)
           onReleased:root.released(mouse)
            id:mourse
            onClicked:{ root.clicked(mouse);root.click(mouse)}
            onCanceled: root.canceled()
            onDoubleClicked: root.doubleClicked(mouse)
            onPositionChanged:root.positionChanged(mouse)
        }
    }
    layer.enabled: true
    layer.effect: DropShadowBase{
        visible: effect
        enabled: effect
    }
}

