import QtQuick
import QtQuick.Layouts
import "../Label"
import "../Buttons"

Column {
    width: parent.width
    id:root
    spacing: 15
    property alias title: titleL.text
    signal close
    RowLayout{
    width: parent.width
        Item{
        Layout.fillWidth: true
        height: 1
        }
    TitleLabel{
        id:titleL
        Layout.alignment: Qt.AlignHCenter
        text: qsTr("设置")
        font.bold: true
    }
    Item{
    Layout.fillWidth: true
    height: 1
    }
    Item{
        width: height
        height: 50
    CloseButton{
        onClicked: root.close()
    }
    }
}
    EfRectangle{
        width:root.parent.visible?root.parent.width-40:0
        height: 3
        color: "teal"
        Behavior on width {NumberAnimation{duration: 600}}
    }
}

