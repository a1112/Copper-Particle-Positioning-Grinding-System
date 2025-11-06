import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../Api" as Api
import "../../components/btns" as Btns
import "../../cores" as Cores
import "pages"

Popup {
  id: root
  modal: true
  dim: true
  focus: true
  anchors.centerIn: parent
  width: parent ? Math.min(parent.width * 0.9, 1080) : 960
  height: parent ? Math.min(parent.height * 0.9, 720) : 640
  closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

  property bool loading: false
  property string errorText: ""
  property var settingsData: ({
    general: {},
    process: {},
    algorithm: {},
    tools: []
  })

  readonly property var categories: [
    { id: "general", label: qsTr("常规参数"), page: generalPage },
    { id: "process", label: qsTr("工艺参数"), page: processPage },
    { id: "algorithm", label: qsTr("算法参数"), page: algorithmPage },
    { id: "tools", label: qsTr("刀具参数"), page: toolPage }
  ]

  property int currentIndex: 0
  readonly property string currentCategory: categories.length > 0 ? categories[currentIndex].id : ""

  onCurrentIndexChanged: {
    if (Cores.CoreSettings && Cores.CoreSettings.parameterTabIndex !== currentIndex)
      Cores.CoreSettings.parameterTabIndex = currentIndex
  }

  function cloneMap(value) {
    if (!value || typeof value !== "object" || Array.isArray(value))
      return {}
    try {
      return JSON.parse(JSON.stringify(value))
    } catch (err) {
      return {}
    }
  }

  function cloneArray(value) {
    if (!Array.isArray(value))
      return []
    try {
      return JSON.parse(JSON.stringify(value))
    } catch (err) {
      return []
    }
  }

  function applyCachedSettings() {
    if (!Cores.CoreSettings)
      return
    var cachedGeneral = cloneMap(Cores.CoreSettings.parameterGeneral)
    var cachedProcess = cloneMap(Cores.CoreSettings.parameterProcess)
    var cachedAlgorithm = cloneMap(Cores.CoreSettings.parameterAlgorithm)
    var cachedTools = cloneArray(Cores.CoreSettings.parameterTools)
    settingsData = {
      general: cachedGeneral,
      process: cachedProcess,
      algorithm: cachedAlgorithm,
      tools: cachedTools
    }
    generalPage.data = cachedGeneral
    processPage.data = cachedProcess
    algorithmPage.data = cachedAlgorithm
    toolPage.tools = cachedTools
  }

  function persistSettingsCache() {
    if (!Cores.CoreSettings)
      return
    Cores.CoreSettings.parameterGeneral = cloneMap(settingsData.general)
    Cores.CoreSettings.parameterProcess = cloneMap(settingsData.process)
    Cores.CoreSettings.parameterAlgorithm = cloneMap(settingsData.algorithm)
    Cores.CoreSettings.parameterTools = cloneArray(settingsData.tools)
  }

  function refresh() {
    loading = true
    errorText = ""
    if (header.statusLabel)
      header.statusLabel.text = ""
    Api.ApiClient.settingsFetch(function(resp) {
      try {
        settingsData = {
          general: resp.categories && resp.categories.general ? resp.categories.general : {},
          process: resp.categories && resp.categories.process ? resp.categories.process : {},
          algorithm: resp.categories && resp.categories.algorithm ? resp.categories.algorithm : {},
          tools: resp.tools ? resp.tools : []
        }
        generalPage.data = settingsData.general
        processPage.data = settingsData.process
        algorithmPage.data = settingsData.algorithm
        toolPage.tools = settingsData.tools
        persistSettingsCache()
      } catch (err) {
        errorText = qsTr("加载失败: %1").arg(err)
      } finally {
        loading = false
      }
    }, function(status, message) {
      loading = false
      errorText = qsTr("加载失败: %1").arg(message || status)
    })
  }

  function loadSettings() { refresh() }

  function currentPage() {
    if (categories.length === 0)
      return null
    if (currentIndex < 0 || currentIndex >= categories.length)
      return null
    return categories[currentIndex].page
  }

  function collectPayload() {
    var page = currentPage()
    if (!page || !page.collectPayload)
      return {}
    return page.collectPayload()
  }

  function saveCurrent() {
    errorText = ""
    if (header.statusLabel)
      header.statusLabel.text = ""
    var category = currentCategory
    var payload = collectPayload()
    if (category === "tools") {
      Api.ApiClient.settingsSaveTools(payload.tools || [], function(resp) {
        toolPage.tools = resp.tools || []
        settingsData.tools = resp.tools || []
        persistSettingsCache()
        header.statusLabel.text = qsTr("刀具参数已保存")
      }, function(status, message) {
        errorText = qsTr("保存失败: %1").arg(message || status)
      })
      return
    }
    Api.ApiClient.settingsSaveCategory(category, payload, function(resp) {
      var saved = resp.payload || {}
      if (category === "general")
        settingsData.general = saved
      else if (category === "process")
        settingsData.process = saved
      else if (category === "algorithm")
        settingsData.algorithm = saved
      currentPage().data = saved
      persistSettingsCache()
      header.statusLabel.text = qsTr("参数已保存")
    }, function(status, message) {
      errorText = qsTr("保存失败: %1").arg(message || status)
    })
  }

  function exportCurrent() {
    errorText = ""
    if (header.statusLabel)
      header.statusLabel.text = ""
    var category = currentCategory
    if (category === "tools") {
      exportDialog.openWithText(JSON.stringify(toolPage.collectPayload().tools || [], null, 2))
      header.statusLabel.text = qsTr("刀具参数已导出")
      return
    }
    Api.ApiClient.settingsExportCategory(category, function(resp) {
      var text = resp.content || ""
      exportDialog.openWithText(text)
      header.statusLabel.text = qsTr("参数已导出")
    }, function(status, message) {
      errorText = qsTr("导出失败: %1").arg(message || status)
    })
  }

  function importCurrent() {
    errorText = ""
    if (header.statusLabel)
      header.statusLabel.text = ""
    importDialog.content = ""
    importDialog.open()
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 20
    spacing: 16
    SettingPageHead { id: header }

    RowLayout {
      Layout.fillWidth: true
      Layout.fillHeight: true
      spacing: 12

      ListView {
        id: categoryList
        Layout.preferredWidth: 140
        Layout.fillHeight: true
        clip: true
        model: categories
        delegate: Rectangle {
          width: categoryList.width
          height: 44
          color: index === root.currentIndex ? Cores.CoreStyle.accent : "#1f2937"
          radius: 6
          border.color: index === root.currentIndex ? Cores.CoreStyle.accent : "#374151"
          Text {
            anchors.centerIn: parent
            text: modelData.label
            color: index === root.currentIndex ? "#000000" : "#d1d5db"
          }
          MouseArea {
            anchors.fill: parent
            onClicked: root.currentIndex = index
          }
        }
      }

      StackLayout {
        id: pageStack
        Layout.fillWidth: true
        Layout.fillHeight: true
        currentIndex: root.currentIndex

        GeneralSettingsPage {
          id: generalPage
          Layout.fillWidth: true
          Layout.fillHeight: true
        }

        ProcessSettingsPage {
          id: processPage
          Layout.fillWidth: true
          Layout.fillHeight: true
        }

        AlgorithmSettingsPage {
          id: algorithmPage
          Layout.fillWidth: true
          Layout.fillHeight: true
        }

        ToolSettingsPage {
          id: toolPage
          Layout.fillWidth: true
          Layout.fillHeight: true
        }
      }
    }

    Label {
      Layout.fillWidth: true
      color: "#f87171"
      text: errorText
      visible: errorText.length > 0
    }
  }

  Dialog {
    id: exportDialog
    modal: true
    standardButtons: Dialog.Ok
    title: qsTr("导出结果")
    property string textValue: ""

    function openWithText(value) {
      textValue = value
      open()
    }

    contentItem: TextArea {
      text: exportDialog.textValue
      readOnly: true
      wrapMode: TextArea.WrapAnywhere
      selectByMouse: true
      implicitWidth: 540
      implicitHeight: 320
    }
  }

  Dialog {
    id: importDialog
    modal: true
    standardButtons: Dialog.Ok | Dialog.Cancel
    title: qsTr("导入 YAML")
    property string content: ""

    onAccepted: {
      if (root.currentCategory === "tools") {
        try {
          var parsed = JSON.parse(content)
          if (!Array.isArray(parsed))
            throw new Error("JSON必须为数组")
          toolPage.importFromArray(parsed)
          settingsData.tools = cloneArray(parsed)
          persistSettingsCache()
          header.statusLabel.text = qsTr("刀具参数已导入")
        } catch (err) {
          errorText = qsTr("导入失败: %1").arg(err)
        }
        return
      }
      Api.ApiClient.settingsImportCategory(root.currentCategory, content, function(resp) {
        var payload = resp.payload || {}
        if (root.currentCategory === "general") {
          settingsData.general = payload
          generalPage.data = payload
        } else if (root.currentCategory === "process") {
          settingsData.process = payload
          processPage.data = payload
        } else if (root.currentCategory === "algorithm") {
          settingsData.algorithm = payload
          algorithmPage.data = payload
        }
        persistSettingsCache()
        header.statusLabel.text = qsTr("参数已导入")
      }, function(status, message) {
        errorText = qsTr("导入失败: %1").arg(message || status)
      })
    }

    contentItem: TextArea {
      text: importDialog.content
      wrapMode: TextArea.WrapAnywhere
      selectByMouse: true
      onTextChanged: importDialog.content = text
      implicitWidth: 540
      implicitHeight: 320
      placeholderText: qsTr("在此粘贴 YAML/JSON 内容后点击确定导入")
    }
  }

  Component.onCompleted: {
    applyCachedSettings()
    var tabIndex = Cores.CoreSettings ? Cores.CoreSettings.parameterTabIndex : 0
    if (tabIndex < 0 || tabIndex >= categories.length)
      tabIndex = 0
    currentIndex = tabIndex
    refresh()
  }
}
