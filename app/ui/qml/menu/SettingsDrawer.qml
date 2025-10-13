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
  dim:true
  // Basic panel content

    ColumnLayout {
      anchors.fill: parent
      anchors.margins: 12
      spacing: 10
      Label {
        text: "设置";
        font.bold: true;
        font.pixelSize: 25
        Layout.alignment: Qt.AlignHCenter

      }

      // API host
      RowLayout {
        Label { text: "API 地址"; Layout.preferredWidth: 90 }
        TextField {
          Layout.fillWidth: true
          text: Cores.CoreSettings ? Cores.CoreSettings.apiHost : ""
          onTextChanged: if (Cores.CoreSettings) Cores.CoreSettings.apiHost = text
          placeholderText: "127.0.0.1"
        }
      }

      // API port
      RowLayout {
        Label { text: "API 端口"; Layout.preferredWidth: 90 }
        SpinBox {
          from: 1; to: 65535
          value: Cores.CoreSettings ? Cores.CoreSettings.apiPort : 8010
          onValueModified: if (Cores.CoreSettings) Cores.CoreSettings.apiPort = value
        }
      }
    Item{
      Layout.fillWidth: true
      Layout.fillHeight: true
    }
      // Theme switching
      GroupBox {
        title: "主题"
        Layout.fillWidth: true
        ColumnLayout {
          spacing: 6
          RowLayout {
            spacing: 10
            Label { text: "当前:"; color: Cores.CoreStyle.muted }
            Label { text: Cores.CoreStyle.theme; color: Cores.CoreStyle.accent }
            Rectangle { width: 14; height: 14; radius: 3; color: Cores.CoreStyle.primary }
            Rectangle { width: 14; height: 14; radius: 3; color: Cores.CoreStyle.accent }
          }
                    RowLayout {
            spacing: 8
            Repeater {
              model: [
                { key: "techBlue", label: "蓝", color: "#2563eb" },
                { key: "emerald", label: "绿", color: "#10b981" },
                { key: "amber", label: "橙", color: "#f59e0b" },
                { key: "nightPurple", label: "紫", color: "#8b5cf6" },
                { key: "graphite", label: "灰", color: "#64748b" }
              ]
              delegate: Rectangle {
                width: 56; height: 28; radius: 4
                color: modelData.color
                border.color: Cores.CoreStyle.border
                border.width: (Cores.CoreStyle.theme===modelData.key ? 2 : 1)
                opacity: 0.95
                Text { anchors.centerIn: parent; text: modelData.label; color: "#ffffff"; font.pixelSize: 12 }
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
      }

      Item { Layout.fillHeight: true }

      RowLayout {
        Button { text: "关闭"; onClicked: settingsDrawer.close() }
        Item { Layout.fillWidth: true }
      }
    }








