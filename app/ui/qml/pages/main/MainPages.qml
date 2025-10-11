import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../cores" as Cores
import "test_page"
import "real_page"

import "debug_page"
import "user_page"
//主显示区域
Item {
    StackLayout{
        anchors.fill: parent
        currentIndex: Cores.CoreState.selectedTabIndex
        RealPageView{}
        UserPageView{}
        DebugPageView{}
        TestPageView{}
    }
}
