import QtQuick
import QtQuick.Controls
Tumbler {
    MouseArea{
    acceptedButtons: Qt.MidButton
    hoverEnabled: true
    anchors.fill: parent
    onWheel: {
    let i= wheel.angleDelta.y>0?1:-1
        if(parent.currentIndex==0&&i<0){
        parent.currentIndex=parent.count-1
        }
        else if(parent.currentIndex== parent.count-1 &&i>0){
                parent.currentIndex=0
        }
        else {
            parent.currentIndex+=i
        }
    }
    }
}

