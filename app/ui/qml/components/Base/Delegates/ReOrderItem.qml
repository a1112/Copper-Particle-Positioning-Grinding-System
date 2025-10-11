import QtQuick
Item {
    id: root
    property Item homeTarget:parent
    property Item dropItem
    property int elementIndex: index
    property string theName
    property int numer
    property alias dropArea: dropArea
    property alias active : dragHandler.active
    width: dragRectangle.width
    height: dragRectangle.height
    property bool is_grid: false

    property bool yAxis_enabled: is_grid?true:!orientation
    property bool xAxis_enabled: is_grid?true:orientation
    signal reorder(int to, int from)
    Item{
        id: dragRectangle
        anchors.top: parent.top
        anchors.left: parent.left
        Drag.source:root
        Drag.active: dragHandler.active
        Drag.imageSource: ""
//        Rectangle{
//            color: "red"
//            width: 10
//            height: 10
//            x:dragRectangle.width/2
//            y:dragRectangle.height/2
//        }
    DragHandler{
        id:dragHandler
    yAxis.enabled: yAxis_enabled
    xAxis.enabled: xAxis_enabled
    }
    Component.onCompleted: {
        dropItem.parent=dragRectangle
        dragRectangle.width=dropItem.width
        dragRectangle.height=dropItem.height
        dragRectangle.width=Qt.binding(()=>dropItem.width)
        dragRectangle.height=Qt.binding(()=>dropItem.height)
    }
    }
    Item{
        x: width * - 0.5
        y: height * - 0.5
                anchors.fill: root
//                color: "red"
    DropArea {
        x: width * - 0.5
        y: height * - 0.5
        id: dropArea
        width: parent.width
        height: parent.height
        property real drag_x: 0
        property real drag_y: 0
        onEntered: {
            if (drag.source.elementIndex !== elementIndex) {
                root.reorder(drag.source.elementIndex, elementIndex)
                drag.accept(Qt.MoveAction)
            }
        }
//        onDropped: {
//            if (drag.source.elementIndex !== elementIndex) {
//                root.reorder(drag.source.elementIndex, elementIndex)
//                drag.accept(Qt.MoveAction)
//            }
//        }
    }
    }
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
AnchorAnimation{duration: 20;easing.type: Easing.OutBack}
        }
    ]
}

