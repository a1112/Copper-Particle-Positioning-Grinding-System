import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../cores" as Cores
import "../../../components/Card"
import "../../../components/Base"

CardHead {
  id: headRoot
  Layout.fillWidth: true
  property alias title: title_id.text
  property var infoViewCore: null

  RowLayout {
    anchors.fill: parent

    CardTitleLabel {
      id:title_id
      text: qsTr("信息")
    }
    Item { Layout.fillWidth: true }

    ItemDelegateBase {
      id: settingsButton
      text: qsTr("显示设置")
      onClicked: {
        filterMenu.anchorItem = settingsButton
        filterMenu.infoViewCore = headRoot.infoViewCore
        filterMenu.popup()
      }
    }
  }

  FilterMenu {
    id: filterMenu
    infoViewCore: headRoot.infoViewCore
  }
}
