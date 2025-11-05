import QtQuick
import QtQuick.Controls
import "../../../../cores" as Cores
Item {
    anchors.fill: parent
    BusyIndicator {
      anchors.centerIn: parent
      running: root.isLoading
      visible: running
      width: 48
      height: 48
    }

    Label {
      visible: root.hasError
      anchors.horizontalCenter: parent.horizontalCenter
      anchors.bottom: parent.bottom
      anchors.bottomMargin: 12
      text: root.errorString.length > 0 ? root.errorString : qsTr("模型加载失败")
      color: Cores.CoreStyle.danger
      font.pixelSize: 13
    }
}
