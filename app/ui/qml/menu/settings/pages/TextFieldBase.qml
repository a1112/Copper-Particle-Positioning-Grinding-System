import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

TextField {
    id: control
    implicitHeight: 35

    // Dirty indicator is driven by parent pages comparing current vs saved values.
    property bool dirty: false
    property color dirtyColor: "#facc15"
    property color normalBorderColor: "#334155"
    property color focusBorderColor: "#60a5fa"
    property color baseBackground: "#0f172a"
    property color disabledBackground: "#1f2937"
    property color baseTextColor: "#e5e7eb"

    color: baseTextColor
    padding: 8

    background: Rectangle {
        radius: 4
        color: control.enabled ? control.baseBackground : control.disabledBackground
        border.width: 1
        border.color: control.dirty
                      ? control.dirtyColor
                      : (control.activeFocus ? control.focusBorderColor : control.normalBorderColor)
    }
}
