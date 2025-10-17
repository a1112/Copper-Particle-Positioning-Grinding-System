import QtQuick
import QtQuick.Controls
import "../../cores" as Cores
 Row{
     spacing: 5
    Label{
        anchors.verticalCenter: parent.verticalCenter
        font.bold: true
        font.pointSize: 15
        text: "模式:"
    }
    ComboBox{
        height: Cores.CoreStyle.headComboBoxHeigh
        model: Cores.CoreUI.allRunModel
        currentIndex: Cores.CoreState
    }
}
