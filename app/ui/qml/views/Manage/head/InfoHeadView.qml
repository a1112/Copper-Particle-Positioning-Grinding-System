import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../cores" as Cores
import "../../../components/Card"
import "../../../components/Base"

CardHead {
  id: headRoot
  Layout.fillWidth: true

  property var infoViewCore: null

  RowLayout {
    anchors.fill: parent

    Label { text: qsTr("信息"); color: Cores.CoreStyle.text; font.pixelSize: 14 }
    Item { Layout.fillWidth: true }

    ItemDelegateBase {
      id: settingsButton
      text: qsTr("显示设置")
      onClicked: {
        filterMenu.anchorItem = settingsButton
        filterMenu.infoViewCore = headRoot.infoViewCore
        filterMenu.open()
      }
    }
  }

  FilterMenu {
    id: filterMenu
    infoViewCore: headRoot.infoViewCore
  }
}
