import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../cores" as Cores

// Right-side settings drawer
Drawer {
  id: settingsDrawer
  edge: Qt.RightEdge
  width: Math.min(380, parent ? parent.width * 0.36 : 380)
  height: parent ? parent.height : 600
  modal: false
  interactive: true
  focus: true
  dim: true

  function _languageCode(raw) {
    var code = raw
    if (code === undefined)
      code = "zh_CN"
    if (code === null)
      code = "zh_CN"
    if (code === "")
      code = "zh_CN"
    return code
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 12
    spacing: 10

    Label {
      text: qsTr("设置")
      font.bold: true
      font.pixelSize: 25
      Layout.alignment: Qt.AlignHCenter
    }

    // API host
    RowLayout {
      Label {
        text: qsTr("API 地址")
        Layout.preferredWidth: 90
      }
      TextField {
        Layout.fillWidth: true
        text: Cores.CoreSettings ? Cores.CoreSettings.apiHost : ""
        onTextChanged: if (Cores.CoreSettings) Cores.CoreSettings.apiHost = text
        placeholderText: "127.0.0.1"
      }
    }

    // API port
    RowLayout {
      Label {
        text: qsTr("API 端口")
        Layout.preferredWidth: 90
      }
      SpinBox {
        from: 1
        to: 65535
        value: Cores.CoreSettings ? Cores.CoreSettings.apiPort : 8010
        onValueModified: if (Cores.CoreSettings) Cores.CoreSettings.apiPort = value
      }
    }

    // Language selector
    GroupBox {
      id: languageGroup
      title: qsTr("语言")
      Layout.fillWidth: true

      ColumnLayout {
        spacing: 6

        RowLayout {
          spacing: 8
          Label {
            text: qsTr("当前:")
            color: Cores.CoreStyle.muted
          }
          Label {
            text: {
              var code = settingsDrawer._languageCode(Cores.CoreSettings ? Cores.CoreSettings.language : undefined)
              return i18n ? i18n.displayName(code) : code
            }
            color: Cores.CoreStyle.accent
          }
        }

        ComboBox {
          id: languageCombo
          Layout.fillWidth: true
          textRole: "label"
          valueRole: "code"
          model: i18n ? i18n.availableLanguages : []

          Component.onCompleted: {
            const code = settingsDrawer._languageCode(Cores.CoreSettings ? Cores.CoreSettings.language : undefined)
            if (i18n && i18n.currentLanguage !== code) {
              i18n.currentLanguage = code
            }
            const idx = languageCombo.indexOfValue(code)
            if (idx >= 0) {
              languageCombo.currentIndex = idx
            }
          }

          onActivated: function(index) {
            if (!model)
              return
            if (index < 0)
              return
            if (index >= model.length)
              return
            const item = model[index]
            if (!item) {
              return
            }
            if (Cores.CoreSettings.language !== item.code) {
              Cores.CoreSettings.language = item.code
            }
            if (i18n && i18n.currentLanguage !== item.code) {
              i18n.currentLanguage = item.code
            }
          }
        }
      }

      Connections {
        target: Cores.CoreSettings
        function onLanguageChanged() {
          const code = settingsDrawer._languageCode(Cores.CoreSettings ? Cores.CoreSettings.language : undefined)
          const idx = languageCombo.indexOfValue(code)
          if (idx >= 0 && languageCombo.currentIndex !== idx) {
            languageCombo.currentIndex = idx
          }
          if (i18n && i18n.currentLanguage !== code) {
            i18n.currentLanguage = code
          }
        }
      }

      Connections {
        target: i18n
        function onLanguageChanged() {
          const code = settingsDrawer._languageCode(i18n ? i18n.currentLanguage : undefined)
          const idx = languageCombo.indexOfValue(code)
          if (idx >= 0 && languageCombo.currentIndex !== idx) {
            languageCombo.currentIndex = idx
          }
          if (Cores.CoreSettings.language !== code) {
            Cores.CoreSettings.language = code
          }
        }
      }
    }

    Item {
      Layout.fillWidth: true
      height: 4
    }

    // Theme switching
    GroupBox {
      id: themeGroup
      title: qsTr("主题")
      Layout.fillWidth: true
      readonly property var options: [
        { key: "techBlue", label: qsTr("科技蓝"), color: "#2563eb" },
        { key: "emerald", label: qsTr("翡翠绿"), color: "#10b981" },
        { key: "amber", label: qsTr("琥珀金"), color: "#f59e0b" },
        { key: "nightPurple", label: qsTr("夜紫"), color: "#8b5cf6" },
        { key: "graphite", label: qsTr("石墨灰"), color: "#64748b" }
      ]

      function themeLabel(key) {
        for (let i = 0; i < themeGroup.options.length; ++i) {
          if (themeGroup.options[i].key === key) {
            return themeGroup.options[i].label
          }
        }
        return key
      }

      ColumnLayout {
        spacing: 6

        RowLayout {
          spacing: 10
          Label {
            text: qsTr("当前:")
            color: Cores.CoreStyle.muted
          }
          Label {
            text: themeGroup.themeLabel(Cores.CoreStyle.theme)
            color: Cores.CoreStyle.accent
          }
          Rectangle { width: 14; height: 14; radius: 3; color: Cores.CoreStyle.primary }
          Rectangle { width: 14; height: 14; radius: 3; color: Cores.CoreStyle.accent }
        }

        RowLayout {
          spacing: 8
          Repeater {
            model: themeGroup.options
            delegate: Rectangle {
              width: 56
              height: 28
              radius: 4
              color: modelData.color
              border.color: Cores.CoreStyle.border
              border.width: Cores.CoreStyle.theme === modelData.key ? 2 : 1
              opacity: 0.95

              Text {
                anchors.centerIn: parent
                text: modelData.label
                color: "#ffffff"
                font.pixelSize: 12
              }

              MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: Cores.CoreStyle.applyTheme(modelData.key)
              }
            }
          }
        }
      }
    }

    Item { Layout.fillHeight: true }

    RowLayout {
      Button {
        text: qsTr("关闭")
        onClicked: settingsDrawer.close()
      }
      Item { Layout.fillWidth: true }
    }
  }
}
