import QtQuick
import QtQuick.Controls.Material
import "../../cores" as Cores
TabBar {
    // 使用不同的 Material 主题颜色
    currentIndex: Cores.CoreState.selectedTabIndex
    onCurrentIndexChanged:  Cores.CoreState.selectedTabIndex=currentIndex
    Repeater{
        model: Cores.CoreUI.pageModels
        TabButton{
            text: modelData
        }
    }
}
