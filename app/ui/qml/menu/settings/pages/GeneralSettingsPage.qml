import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
  id: page
  property var data: ({})
  property bool allowDeviceControl: false
  property bool allowJog: false

  function collectPayload() {
    var payload = {}
    if (data && typeof data === "object" && !Array.isArray(data)) {
      try {
        payload = JSON.parse(JSON.stringify(data))
      } catch (err) {
        payload = {}
      }
    }
    var deviceArea = payload.device_area
    if (!deviceArea || typeof deviceArea !== "object")
      deviceArea = {}
    deviceArea.allow_direct_control = !!allowDeviceControl
    deviceArea.allow_jog = !!allowJog
    payload.device_area = deviceArea
    return payload
  }

  function _deviceArea() {
    if (!data || typeof data !== "object")
      return {}
    if (data.device_area && typeof data.device_area === "object")
      return data.device_area
    if (data.deviceArea && typeof data.deviceArea === "object")
      return data.deviceArea
    return {}
  }

  function _syncFromData() {
    var area = _deviceArea()
    if (area.hasOwnProperty("allow_direct_control"))
      allowDeviceControl = !!area.allow_direct_control
    else if (area.hasOwnProperty("allowDirectControl"))
      allowDeviceControl = !!area.allowDirectControl
    else
      allowDeviceControl = false

    if (area.hasOwnProperty("allow_jog"))
      allowJog = !!area.allow_jog
    else if (area.hasOwnProperty("allowJog"))
      allowJog = !!area.allowJog
    else
      allowJog = false
  }

  function _writeBack() {
    data = collectPayload()
  }

  onDataChanged: _syncFromData()
  Component.onCompleted: _syncFromData()

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 16
    spacing: 12
    Label {
      text: qsTr("常规参数设置")
      font.pixelSize: 18
      font.bold: true
      color: "#f8fafc"
    }
    Rectangle {
      Layout.fillWidth: true
      color: "#0f172a"
      radius: 8
      border.color: "#1e293b"
      border.width: 1

      ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Label {
          text: qsTr("设备控制区")
          font.pixelSize: 16
          font.bold: true
          color: "#f8fafc"
        }

        RowLayout {
          Layout.fillWidth: true
          spacing: 12
          Label {
            text: qsTr("允许直接控制设备")
            color: "#cbd5f5"
            Layout.fillWidth: true
          }
          Switch {
            checked: page.allowDeviceControl
            onToggled: {
              page.allowDeviceControl = checked
              if (!checked)
                page.allowJog = false
              page._writeBack()
            }
          }
        }
        Label {
          text: qsTr("启用后可在界面中显示设备控制与气缸操作区域。")
          color: "#94a3b8"
          wrapMode: Text.Wrap
        }

        RowLayout {
          Layout.fillWidth: true
          spacing: 12
          Label {
            text: qsTr("允许点动")
            color: "#cbd5f5"
            Layout.fillWidth: true
          }
          Switch {
            enabled: page.allowDeviceControl
            checked: page.allowJog
            onToggled: {
              page.allowJog = checked
              page._writeBack()
            }
          }
        }
        Label {
          text: qsTr("关闭后即使显示控制区，仍禁止发送点动指令。")
          color: "#94a3b8"
          wrapMode: Text.Wrap
        }
      }
    }
    Item { Layout.fillHeight: true }
  }
}
