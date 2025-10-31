import QtQuick
Item {
    id: root
    property Item homeTarget:parent
    property Component dropItem
    property int elementIndex: index
    property var orientation:-1
    readonly property bool allowVertical: orientation === -1 ? true : orientation === ListView.Vertical
    readonly property bool allowHorizontal: orientation === -1 ? true : orientation === ListView.Horizontal
    property string theName
    z:active?1:0
    property int numer
    property alias dropArea: dropArea
    property bool active: dragHandler.active
    width: dragRectangle.width
    height: dragRectangle.height
    signal reorder(int to, int from)

    Loader{
        Drag.source:root
        Drag.active: dragHandler.active
        id: dragRectangle
        anchors.top: parent.top
//        anchors.bottom: parent.bottom
        anchors.left: parent.left
//        anchors.right: parent.right
    sourceComponent: dropItem

    DragHandler{
        id:dragHandler
    yAxis.enabled: root.allowVertical
    xAxis.enabled: root.allowHorizontal
    }
    }

    DropArea {
        id: dropArea
        width: parent.width
        height: parent.height
        // Why is the X/Y offset this way?
        x: width * - 0.5
        onEntered: {
            if (drag.source.elementIndex !== elementIndex) {
                root.reorder(drag.source.elementIndex, elementIndex)
                drag.accept(Qt.MoveAction)
            }
        }
    }


//    MouseArea {
//        id: ma
//        acceptedButtons: Qt.NoButton
//        anchors.fill: parent
//        drag.target: dragRectangle
//        drag.axis: Drag.XAxis
//        preventStealing :true
//        propagateComposedEvents:false
//    }

    states: [
        State {
            name: "dragging"
            when: dragHandler.active
            ParentChange { target: dragRectangle; parent: root.homeTarget }
            AnchorChanges { target: dragRectangle; anchors.top: undefined; anchors.right: undefined; anchors.bottom: undefined; anchors.left: undefined }
        }
    ]
    transitions: [
        Transition {
            from: "dragging"
            to: "*"
AnchorAnimation{duration: 300;easing.type: Easing.OutBack}
        }
    ]
}

