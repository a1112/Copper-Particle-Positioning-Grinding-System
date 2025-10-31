import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../Api" as Api
import "../Base" as Base
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

  property int currentIndex: 2
  readonly property string currentCategory: categories[currentIndex].id

  function refresh() {
    loading = true
    errorText = ""
    if (infoLabel)
      infoLabel.text = ""
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
    if (infoLabel)
      infoLabel.text = ""
    var category = currentCategory
    var payload = collectPayload()
    if (category === "tools") {
      Api.ApiClient.settingsSaveTools(payload.tools || [], function(resp) {
        toolPage.tools = resp.tools || []
        settingsData.tools = resp.tools || []
        infoLabel.text = qsTr("刀具参数已保存")
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
      infoLabel.text = qsTr("参数已保存")
    }, function(status, message) {
      errorText = qsTr("保存失败: %1").arg(message || status)
    })
  }

  function exportCurrent() {
    errorText = ""
    if (infoLabel)
      infoLabel.text = ""
    var category = currentCategory
    if (category === "tools") {
      exportDialog.openWithText(JSON.stringify(toolPage.collectPayload().tools || [], null, 2))
      infoLabel.text = qsTr("刀具参数已导出")
      return
    }
    Api.ApiClient.settingsExportCategory(category, function(resp) {
      var text = resp.content || ""
      exportDialog.openWithText(text)
      infoLabel.text = qsTr("参数已导出")
    }, function(status, message) {
      errorText = qsTr("导出失败: %1").arg(message || status)
    })
  }

  function importCurrent() {
    errorText = ""
    if (infoLabel)
      infoLabel.text = ""
    importDialog.content = ""
    importDialog.open()
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 20
    spacing: 16

    RowLayout {
      Layout.fillWidth: true
      spacing: 12

      Label {
        text: qsTr("参数设置中心")
        font.bold: true
        font.pixelSize: 20
        color: "#f1f5f9"
      }

      Item { Layout.fillWidth: true }

      Label {
        id: infoLabel
        color: "#9AA5B1"
        text: ""
      }

      Button {
        text: loading ? qsTr("刷新中…") : qsTr("刷新")
        enabled: !loading
        onClicked: refresh()
      }

      Button {
        text: qsTr("导入")
        enabled: !loading
        onClicked: importCurrent()
      }

      Button {
        text: qsTr("导出")
        enabled: !loading
        onClicked: exportCurrent()
      }

      Button {
        text: qsTr("保存")
        enabled: !loading
        onClicked: saveCurrent()
      }

      Button {
        text: qsTr("关闭")
        onClicked: root.close()
      }
    }

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

  BusyIndicator {
    anchors.centerIn: parent
    visible: loading
    running: loading
    z: 10
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
          infoLabel.text = qsTr("刀具参数已导入")
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
        infoLabel.text = qsTr("参数已导入")
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

  Component.onCompleted: refresh()
}
