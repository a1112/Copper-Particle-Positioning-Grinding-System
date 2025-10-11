import QtQuick
import "../../cores" as Cores`nimport QtQuick.Controls
import "../../cores" as Cores`nItemDelegateButtonBase {
    source: Cores.CoreStyle.getIconSource("qml/resource/icon/AI.png")

    Menu{

        id:aiMenu

        MenuItem{
            text: qsTr("重算")
            onClicked: {
                //   图像重算
                console.log("图像重算")
                control.refreshDefectViewBySteelId_predict(Cores.CoreState.currentSteelId)
            }
        }

        MenuItem{
            text: qsTr("设置...")
        }
    }

    onClicked: {
        aiMenu.popup()
    }
}


