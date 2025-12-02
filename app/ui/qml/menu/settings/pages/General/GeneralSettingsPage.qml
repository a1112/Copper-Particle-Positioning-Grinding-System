import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../"
import "../../../../Api" as Api

Pane {
  id: page
  property var data: ({})
  property var savedData: ({})
  property bool _internalChange: false
  property color dirtyColor: "#facc15"
  property bool allowDeviceControl: false
  property bool allowJog: false
  property bool estopDoubleConfirm: true
  property string cameraProfile: "sim"
  property string cameraSerial: ""

  ListModel { id: cameraModel }

  function cloneMap(value) {
    if (!value || typeof value !== "object" || Array.isArray(value))
      return {}
    try {
      return JSON.parse(JSON.stringify(value))
    } catch (err) {
      return {}
    }
  }

  function colorWhenDirty(dirty, normalColor) {
    return dirty ? dirtyColor : normalColor
  }

  function valuesEqual(a, b) {
    if (a === b)
      return true
    if (typeof a === "boolean" || typeof b === "boolean")
      return !!a === !!b
    var numA = Number(a)
    var numB = Number(b)
    if (!isNaN(numA) && !isNaN(numB))
      return numA === numB
    return String(a || "") === String(b || "")
  }

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

    var safety = payload.safety
    if (!safety || typeof safety !== "object")
      safety = {}
    safety.estop_double_confirm = !!estopDoubleConfirm
    payload.safety = safety
    return payload
  }

  function _deviceAreaFrom(source) {
    if (!source || typeof source !== "object")
      return {}
    if (source.device_area && typeof source.device_area === "object")
      return source.device_area
    if (source.deviceArea && typeof source.deviceArea === "object")
      return source.deviceArea
    return {}
  }

  function _deviceArea() { return _deviceAreaFrom(data) }
  function _savedDeviceArea() { return _deviceAreaFrom(savedData) }

  function _cameraSettings() {
    if (!data || typeof data !== "object")
      return {}
    if (data.camera && typeof data.camera === "object")
      return data.camera
    if (data.camera_settings && typeof data.camera_settings === "object")
      return data.camera_settings
    return {}
  }

  function _savedCameraSettings() {
    if (!savedData || typeof savedData !== "object")
      return {}
    if (savedData.camera && typeof savedData.camera === "object")
      return savedData.camera
    if (savedData.camera_settings && typeof savedData.camera_settings === "object")
      return savedData.camera_settings
    return {}
  }

  function _safetySettings() {
    if (!data || typeof data !== "object")
      return {}
    if (data.safety && typeof data.safety === "object")
      return data.safety
    if (data.safe_settings && typeof data.safe_settings === "object")
      return data.safe_settings
    if (data.estop_double_confirm !== undefined)
      return { estop_double_confirm: data.estop_double_confirm }
    return {}
  }

  function _savedSafetySettings() {
    if (!savedData || typeof savedData !== "object")
      return {}
    if (savedData.safety && typeof savedData.safety === "object")
      return savedData.safety
    if (savedData.safe_settings && typeof savedData.safe_settings === "object")
      return savedData.safe_settings
    if (savedData.estop_double_confirm !== undefined)
      return { estop_double_confirm: savedData.estop_double_confirm }
    return {}
  }

  function _savedAllowDeviceControl() {
    var area = _savedDeviceArea()
    if (area.hasOwnProperty("allow_direct_control"))
      return !!area.allow_direct_control
    if (area.hasOwnProperty("allowDirectControl"))
      return !!area.allowDirectControl
    return false
  }

  function _savedAllowJog() {
    var area = _savedDeviceArea()
    if (area.hasOwnProperty("allow_jog"))
      return !!area.allow_jog
    if (area.hasOwnProperty("allowJog"))
      return !!area.allowJog
    return false
  }

  function _savedCameraProfileId() {
    var camera = _savedCameraSettings()
    if (camera.profile)
      return camera.profile
    return "sim"
  }

  function _savedCameraSerial() {
    var camera = _savedCameraSettings()
    return camera.serial || ""
  }

  function _savedEstopDoubleConfirm() {
    var safety = _savedSafetySettings()
    if (safety.hasOwnProperty("estop_double_confirm"))
      return !!safety.estop_double_confirm
    return true
  }

  function isAllowDeviceControlDirty() { return !valuesEqual(allowDeviceControl, _savedAllowDeviceControl()) }
  function isAllowJogDirty() { return !valuesEqual(allowJog, _savedAllowJog()) }
  function isCameraProfileDirty() { return !valuesEqual(cameraProfile, _savedCameraProfileId()) }
  function isCameraSerialDirty() { return !valuesEqual(cameraSerial, _savedCameraSerial()) }
  function isEstopDirty() { return !valuesEqual(estopDoubleConfirm, _savedEstopDoubleConfirm()) }

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

    var safety = _safetySettings()
    if (safety.hasOwnProperty("estop_double_confirm"))
      estopDoubleConfirm = !!safety.estop_double_confirm
    else
      estopDoubleConfirm = true
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
    _internalChange = true
    data = collectPayload()
    _internalChange = false
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

  onDataChanged: {
    if (!_internalChange)
      savedData = cloneMap(data)
    _syncFromData()
  }
  Component.onCompleted: {
    savedData = cloneMap(data)
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
            color: colorWhenDirty(isAllowDeviceControlDirty(), "#cbd5f5")
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
            color: colorWhenDirty(isAllowJogDirty(), "#cbd5f5")
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
      title: qsTr("安全设置")
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
            text: qsTr("急停二次确认")
            color: colorWhenDirty(isEstopDirty(), "#cbd5f5")
            Layout.fillWidth: true
          }
          Switch {
            checked: page.estopDoubleConfirm
            onToggled: {
              page.estopDoubleConfirm = checked
              page._writeBack()
            }
          }
        }
        Label {
          text: qsTr("关闭后点击急停按钮或快捷指令会立即执行急停，请确认周围环境安全。")
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
            color: colorWhenDirty(isCameraProfileDirty(), "#cbd5f5")
            Layout.preferredWidth: 120
          }
          ComboBoxBase {
            dirty: isCameraProfileDirty()
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
            color: colorWhenDirty(isCameraSerialDirty(), "#cbd5f5")
            Layout.preferredWidth: 120
          }
          TextFieldBase {
            dirty: isCameraSerialDirty()
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
