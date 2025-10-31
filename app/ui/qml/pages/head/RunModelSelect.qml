import QtQuick
import QtQuick.Controls
import "../../cores" as Cores
import "../../components/Base" as Base
 Row{
     spacing: 5
    Label{
        anchors.verticalCenter: parent.verticalCenter
        font.bold: true
        font.pointSize: 15
        text: qsTr("模式:")
    }
    Base.ComboBoxBase{
        model: Cores.CoreUI.allRunModel
        currentIndex: Cores.CoreState.currentRunModelIndex
        onCurrentIndexChanged: Cores.CoreState.currentRunModelIndex=currentIndex
    }
}
