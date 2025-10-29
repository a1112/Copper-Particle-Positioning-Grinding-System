pragma Singleton
import QtQuick
import QtCore
import QtQml
import "../Api" as Api
Item {
  id: root

  property int selectedTabIndex: 0

  property int currentRunModelIndex: 0
  readonly property string currentRunModelName: CoreUI.allRunModel[currentRunModelIndex]

  readonly property bool isUseModel: currentRunModelName == "手动"

  property int realViewIndex: 0
  readonly property string realViewName: CoreUI.dataViewModels[realViewIndex]

  property int current2DShowIndex: 0
  readonly property string current2DShowName: CoreUI.allImageType[current2DShowIndex]

  readonly property var imageTypeQueryMap: ({
    "彩色": "color",
    "灰度": "gray",
    "深度": "depth",
    "法线": "normal"
  })

  property string current2dImageSource: ""

  function refreshImageSource() {
    const queryValue = imageTypeQueryMap[current2DShowName] || "color"
    current2dImageSource = Api.Urls.api("image/test") + "?type=" + queryValue + "&ts=" + Date.now()
  }

  Settings {
    id: st
    category: "CoreState"
    property alias selectedTabIndex: root.selectedTabIndex
    property alias currentRunModelIndex: root.currentRunModelIndex
  }

  Timer {
    id: imageRefreshTimer
    interval: 5000
    repeat: true
    running: true
    onTriggered: refreshImageSource()
  }

  Component.onCompleted: refreshImageSource()
  onCurrent2DShowNameChanged: {
    imageRefreshTimer.restart()
    refreshImageSource()
  }
}
