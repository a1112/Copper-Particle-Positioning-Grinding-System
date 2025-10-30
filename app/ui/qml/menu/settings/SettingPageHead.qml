import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

TabBar {
    id: root
    implicitHeight: 40
    TabButton { text: qsTr("常规参数设置") }
    TabButton { text: qsTr("工艺参数设置") }
    TabButton { text: qsTr("算法参数设置") }
    TabButton { text: "刀具参数设置" }
}
