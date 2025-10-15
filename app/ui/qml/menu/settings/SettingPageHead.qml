import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

TabBar {
    id: root
    implicitHeight: 40

    TabButton { text: "任务配置" }
    TabButton { text: "标定设置" }
    TabButton { text: "刀具设置" }
}
