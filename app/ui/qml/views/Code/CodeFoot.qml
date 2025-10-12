import QtQuick
import QtQuick.Controls.Material
import QtQuick.Layouts
import QtCore

import "../../cores" as Cores

Row {
    spacing: 5
    Label { text: (editor.text.length + ' chars'); color: Cores.CoreStyle.muted }
    Item { Layout.fillWidth: true }
}
