import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../../Api" as Api

Pane {
  id: page
  property var data: ({})
  property bool allowDeviceControl: false
  property bool allowJog: false
  property string cameraProfile: "sim"
  property string cameraSerial: ""

  ListModel { id: cameraModel }

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

    var camera = payload.camera
    if (!camera || typeof camera !== "object")
      camera = {}
    camera.profile = cameraProfile || "sim"
    camera.serial = cameraSerial || ""
    payload.camera = camera
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

  function _cameraSettings() {
    if (!data || typeof data !== "object")
      return {}
    if (data.camera && typeof data.camera === "object")
      return data.camera
    if (data.camera_settings && typeof data.camera_settings === "object")
      return data.camera_settings
    return {}
  }

  function _syncFromData() {
    var area = _deviceArea()
    allowDeviceControl = area.hasOwnProperty("allow_direct_control")
                         ? !!area.allow_direct_control
                         : (area.hasOwnProperty("allowDirectControl") ? !!area.allowDirectControl : false)
    allowJog = area.hasOwnProperty("allow_jog")
               ? !!area.allow_jog
               : (area.hasOwnProperty("allowJog") ? !!area.allowJog : false)

    var camera = _cameraSettings()
    if (camera.profile)
      cameraProfile = camera.profile
    cameraSerial = camera.serial || ""
  }

  function _cameraIndexFor(profileId) {
    if (!cameraModel || cameraModel.count === 0)
      return -1
    if (!profileId)
      return 0
    for (var i = 0; i < cameraModel.count; ++i) {
      if (cameraModel.get(i).id === profileId)
        return i
    }
    return 0
  }

  function _writeBack() {
    data = collectPayload()
  }

  function _loadCameraProfiles() {
    Api.ApiClient.visionListCameras(function(resp) {
      cameraModel.clear()
      var profiles = resp.profiles || []
      profiles.forEach(function(item) {
        cameraModel.append({
          id: item.id,
          label: item.label,
          description: item.description || "",
          available: item.available !== false
        })
      })
    }, function(status, message) {
      console.log("visionListCameras failed", status, message)
    })
  }

  onDataChanged: _syncFromData()
  Component.onCompleted: {
    _syncFromData()
    _loadCameraProfiles()
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 2
    spacing: 5
    Label {
      text: qsTr("常规参数设置")
      font.pixelSize: 18
      font.bold: true
      color: "#f8fafc"
    }

    GroupBox {
      Layout.fillWidth: true
      title: qsTr("设备控制区")
      font.pixelSize: 16
      font.bold: true

      ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 12

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

    GroupBox {
      Layout.fillWidth: true
      title: qsTr("3D 相机")
      font.pixelSize: 16
      font.bold: true

      ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 12

        RowLayout {
          Layout.fillWidth: true
          spacing: 12
          Label {
            text: qsTr("相机类型")
            color: "#cbd5f5"
            Layout.preferredWidth: 120
          }
          ComboBox {
            Layout.preferredWidth: 240
            model: cameraModel
            textRole: "label"
            valueRole: "id"
            currentIndex: page._cameraIndexFor(page.cameraProfile)
            onActivated: {
              if (currentValue)
                page.cameraProfile = currentValue
              else if (currentIndex >= 0)
                page.cameraProfile = cameraModel.get(currentIndex).id
              page._writeBack()
            }
          }
          Label {
            Layout.fillWidth: true
            color: "#94a3b8"
            wrapMode: Text.WordWrap
            text: cameraModel.count > 0 && page._cameraIndexFor(page.cameraProfile) >= 0
                  ? (cameraModel.get(page._cameraIndexFor(page.cameraProfile)).description || "")
                  : qsTr("未加载到相机选项，可稍后重试。")
          }
        }

        RowLayout {
          Layout.fillWidth: true
          spacing: 12
          Label {
            text: qsTr("首选序列号")
            color: "#cbd5f5"
            Layout.preferredWidth: 120
          }
          TextField {
            Layout.fillWidth: true
            placeholderText: qsTr("可选：限制连接具体设备")
            text: page.cameraSerial
            onEditingFinished: {
              page.cameraSerial = text
              page._writeBack()
            }
          }
        }
      }
    }

    Item { Layout.fillHeight: true }
  }
}
