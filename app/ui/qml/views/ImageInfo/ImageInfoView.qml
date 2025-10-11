import QtQuick
import "../../Api" as Api
//显示图像
Item {
    Image {
        anchors.fill: parent
        fillMode: Image.PreserveAspectFit
        cache: false
        asynchronous: false
        source: Api
    }


}
