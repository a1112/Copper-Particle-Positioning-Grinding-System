import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


import "../../Base"
import "../../../cores" as Cores
import "../../../components/Base" as Base
import "../../../components/btns" as Btns

BaseHead {
    property bool showRobotArm: false

    RowLayout{
        anchors.fill: parent

        Base.ComboBoxBase{
            model: Cores.CoreUI.allImageType
            visible: Cores.CoreState.realViewName=="2D"
            onCurrentIndexChanged: Cores.CoreState.current2DShowIndex = currentIndex
        }
        MaskSelect{
            visible: Cores.CoreState.realViewName=="2D"
        }
        Item { Layout.fillWidth: true }
        // 机器人模型切换按钮 - 仅在3D视图显示
        Btns.CheckBoxBase {
            visible: Cores.CoreState.realViewName == "3D"
            text: qsTr("机器人")
            checked: root.showRobotArm
            onCheckedChanged: root.showRobotArm = checked
        }
        Label { text: qsTr("视图"); color: Cores.CoreStyle.text; font.pixelSize: 14 }
        Item { Layout.fillWidth: true }
        ViewChiose{
        }
    }
}

