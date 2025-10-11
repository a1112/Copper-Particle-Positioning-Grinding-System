import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
Popup {
    property string viewName:""
    spacing: 0
    padding: 0
    Component.onCompleted: {
    if(viewName)
        runTime[viewName]=this
    }
}

