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
  property string particleMaskSource: ""
  property bool showParticleMask: false
  property bool showPathOverlay: true
  readonly property url fallbackModelSource: Qt.resolvedUrl("../../../../TestData/models/generated_surface.mesh")
  property url localModelMesh: Qt.platform.os === "windows"
                               ? "file:///D:/SaveData/current/generated_surface.mesh"
                               : ""
  property url localModelObj: Qt.platform.os === "windows"
                              ? "file:///D:/SaveData/current/generated_surface.obj"
                              : ""
  property bool usingFallbackModel: false
  property url current3dModelSource: ""

  function refreshImageSource() {
    const queryValue = imageTypeQueryMap[current2DShowName] || "color"
    current2dImageSource = Api.Urls.api("image/test") + "?type=" + queryValue + "&ts=" + Date.now()
    refreshParticleMaskSource()
    refresh3dModelSource()
  }

  function refreshParticleMaskSource() {
    if (!showParticleMask) {
      particleMaskSource = ""
      return
    }
    particleMaskSource = Api.Urls.api("image/mask") + "?ts=" + Date.now()
  }

  function refresh3dModelSource() {
    usingFallbackModel = false
    current3dModelSource = ""
    Qt.callLater(function() {
      if (localModelMesh && localModelMesh.toString().length > 0)
        current3dModelSource = localModelMesh
      else if (localModelObj && localModelObj.toString().length > 0)
        current3dModelSource = localModelObj
      else
        useFallbackModel()
    })
  }

  function useFallbackModel() {
    if (usingFallbackModel)
      return
    usingFallbackModel = true
    current3dModelSource = ""
    Qt.callLater(() => current3dModelSource = fallbackModelSource)
  }

  Settings {
    id: st
    category: "CoreState"
    property alias selectedTabIndex: root.selectedTabIndex
    property alias currentRunModelIndex: root.currentRunModelIndex
  }

  Component.onCompleted: refreshImageSource()
  onCurrent2DShowNameChanged: {
    refreshImageSource()
  }
  onShowParticleMaskChanged: {
    if (showParticleMask)
      refreshParticleMaskSource()
    else
      particleMaskSource = ""
  }
  onLocalModelMeshChanged: refresh3dModelSource()
  onLocalModelObjChanged: refresh3dModelSource()

  function refreshDataSources() {
    refreshImageSource()
  }
}
