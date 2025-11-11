import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

import "../../../Api" as Api
import "../../../views/Calibration" as Calibration

Item {
  id: root
  Layout.fillWidth: true
  Layout.fillHeight: true

  property var parameterSchema: []
  property var parameterValues: ({})
  property string selectedMode: "capture"
  property string folderPath: ""
  property bool running: false
  property string statusText: ""
  property var lastResult: null
  property string selectedCameraProfile: ""

  ListModel { id: cameraModel }

  function _cloneValues() {
    return JSON.parse(JSON.stringify(parameterValues || {}))
  }

  function parameterValue(key, fallback) {
    if (parameterValues && parameterValues.hasOwnProperty(key))
      return parameterValues[key]
    return fallback
  }

  function updateParameter(key, value) {
    var clone = _cloneValues()
    clone[key] = value
    parameterValues = clone
  }

  function urlToPath(url) {
    if (!url)
      return ""
    var text = url.toString ? url.toString() : String(url)
    if (text.startsWith("file:///"))
      text = decodeURIComponent(text.replace("file:///", ""))
    else if (text.startsWith("file://"))
      text = decodeURIComponent(text.replace("file://", ""))
    return text
  }

  function loadDefaults() {
    Api.ApiClient.task1Defaults(function(resp) {
      parameterSchema = resp.parameters || []
      var defaults = {}
      parameterSchema.forEach(function(item) {
        defaults[item.key] = item.default
      })
      parameterValues = defaults

      cameraModel.clear()
      var profiles = resp.camera_profiles || []
      profiles.forEach(function(item) {
        cameraModel.append({
          id: item.id,
          label: item.label,
          description: item.description || "",
          available: item.available !== false
        })
      })
      if (cameraModel.count > 0) {
        selectedCameraProfile = resp.default_camera || cameraModel.get(0).id
      } else {
        selectedCameraProfile = ""
      }
      if (!statusText)
        statusText = qsTr("已加载默认参数。")
    }, function(status, message) {
      statusText = qsTr("无法加载默认配置 (%1): %2").arg(status).arg(message || "")
    })
  }

  function cameraIndexFor(profileId) {
    if (!profileId)
      return cameraModel.count > 0 ? 0 : -1
    for (var i = 0; i < cameraModel.count; ++i) {
      if (cameraModel.get(i).id === profileId)
        return i
    }
    return cameraModel.count > 0 ? 0 : -1
  }

  function runTask1() {
    if (running)
      return
    if (selectedMode === "folder" && (!folderPath || folderPath.length === 0)) {
      statusText = qsTr("请选择包含 src_IMG*_PointCloud 文件的文件夹。")
      return
    }
    running = true
    statusText = selectedMode === "capture"
                  ? qsTr("正在采集并运行算法...")
                  : qsTr("正在加载文件夹并运行算法...")
    var payload = {
      mode: selectedMode,
      overrides: parameterValues,
      build_visuals: true
    }
    if (selectedMode === "folder")
      payload.folder = folderPath
    else
      payload.camera_profile = selectedCameraProfile
    Api.ApiClient.task1Run(payload, function(resp) {
      running = false
      lastResult = resp
      var stamp = Qt.formatDateTime(new Date(), "hh:mm:ss")
      statusText = qsTr("完成 (%1)").arg(stamp)
    }, function(status, message) {
      running = false
      statusText = qsTr("执行失败 (%1): %2").arg(status).arg(message || "")
    })
  }

  Flickable {
    id: scroller
    anchors.fill: parent
    contentWidth: width
    contentHeight: contentColumn.implicitHeight + 32
    clip: true

    ColumnLayout {
      id: contentColumn
      width: scroller.width
      spacing: 16

      Rectangle {
        Layout.fillWidth: true
        radius: 10
        color: "#1e2432"
        border.color: "#2a3142"
        border.width: 1
        Layout.margins: 12

        ColumnLayout {
          anchors.fill: parent
          anchors.margins: 16
          spacing: 12

          Label {
            text: qsTr("测试输入与采集")
            font.pixelSize: 20
            color: "#f8fafc"
          }

          RowLayout {
            Layout.fillWidth: true
            spacing: 12
            Label { text: qsTr("数据来源"); color: "#cbd5f5"; Layout.preferredWidth: 90 }
            RadioButton {
              text: qsTr("相机采集")
              checked: root.selectedMode === "capture"
              onToggled: if (checked) root.selectedMode = "capture"
            }
            RadioButton {
              text: qsTr("加载文件夹")
              checked: root.selectedMode === "folder"
              onToggled: if (checked) root.selectedMode = "folder"
            }
            Item { Layout.fillWidth: true }
          }

          RowLayout {
            Layout.fillWidth: true
            spacing: 12
            Label { text: qsTr("3D 相机"); color: "#cbd5f5"; Layout.preferredWidth: 90 }
            ComboBox {
              id: cameraCombo
              Layout.preferredWidth: 240
              enabled: root.selectedMode === "capture" && cameraModel.count > 0
              model: cameraModel
              textRole: "label"
              valueRole: "id"
              currentIndex: root.cameraIndexFor(root.selectedCameraProfile)
              onActivated: {
                if (cameraCombo.currentValue)
                  root.selectedCameraProfile = cameraCombo.currentValue
                else if (cameraCombo.currentIndex >= 0)
                  root.selectedCameraProfile = cameraModel.get(cameraCombo.currentIndex).id
              }
            }
            Label {
              Layout.fillWidth: true
              color: "#94a3b8"
              text: cameraModel.count > 0 && cameraCombo.currentIndex >= 0
                    ? (cameraModel.get(cameraCombo.currentIndex).description || "")
                    : qsTr("无可用相机。")
              wrapMode: Text.WordWrap
            }
          }

          RowLayout {
            Layout.fillWidth: true
            spacing: 12
            Label { text: qsTr("测试文件夹"); color: "#cbd5f5"; Layout.preferredWidth: 90 }
            TextField {
              Layout.fillWidth: true
              enabled: root.selectedMode === "folder"
              placeholderText: qsTr("例如 D:/SaveData/record/001")
              text: root.folderPath
              onEditingFinished: root.folderPath = text
            }
            Button {
              text: qsTr("浏览")
              enabled: root.selectedMode === "folder"
              onClicked: folderDialog.open()
            }
          }

          Rectangle {
            Layout.fillWidth: true
            radius: 8
            color: "#262c3d"
            border.color: "#31384a"
            ColumnLayout {
              anchors.fill: parent
              anchors.margins: 12
              spacing: 8

              Label { text: qsTr("算法参数"); color: "#e2e8f0"; font.pixelSize: 16 }

              Repeater {
                model: root.parameterSchema
                delegate: RowLayout {
                  Layout.fillWidth: true
                  spacing: 8
                  Label {
                    text: modelData.label || modelData.key
                    Layout.preferredWidth: 200
                    color: "#cbd5f5"
                  }
                  TextField {
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                    text: String(root.parameterValue(modelData.key, modelData.default))
                    selectByMouse: true
                    enabled: true
                    validator:  DoubleValidator {
                                   bottom: modelData.min !== undefined ? modelData.min : -2147483648
                                   top: modelData.max !== undefined ? modelData.max : 2147483647
                                   decimals: 3
                                 }
                    onEditingFinished: {
                      var value = modelData.type === "int" ? parseInt(text) : parseFloat(text)
                      if (isNaN(value))
                        value = modelData.default
                      root.updateParameter(modelData.key, value)
                    }
                  }
                }
              }
            }
          }

          RowLayout {
            Layout.fillWidth: true
            spacing: 12
            Button {
              text: root.running
                    ? qsTr("运行中...")
                    : (root.selectedMode === "capture" ? qsTr("采集并运行") : qsTr("加载并运行"))
              Layout.preferredWidth: 160
              enabled: !root.running && (root.selectedMode === "capture" || root.folderPath.length > 0)
              onClicked: root.runTask1()
            }
            Label {
              Layout.fillWidth: true
              wrapMode: Text.WordWrap
              color: "#f8fafc"
              text: root.statusText
            }
          }
        }
      }

      Rectangle {
        Layout.fillWidth: true
        radius: 10
        color: "#1e2432"
        border.color: "#2a3142"
        Layout.margins: 12

        ColumnLayout {
          anchors.fill: parent
          anchors.margins: 16
          spacing: 12

          Label { text: qsTr("测试结果"); font.pixelSize: 20; color: "#f8fafc" }

          ColumnLayout {
            Layout.fillWidth: true
            visible: !!root.lastResult

            Label {
              text: root.lastResult ? qsTr("源目录: %1").arg(root.lastResult.source_dir) : ""
              color: "#94a3b8"
              wrapMode: Text.WordWrap
            }

            Flow {
              Layout.fillWidth: true
              spacing: 16
              Repeater {
                model: root.lastResult && root.lastResult.metrics
                        ? Object.keys(root.lastResult.metrics).filter(function(key) { return key !== "summary" })
                        : []
                delegate: Rectangle {
                  width: Math.min(180, parent.width / 3)
                  height: 64
                  radius: 6
                  color: "#262c3d"
                  border.color: "#323b4e"
                  Column {
                    anchors.centerIn: parent
                    spacing: 4
                    Label {
                      text: modelData
                      color: "#94a3b8"
                      font.pixelSize: 12
                      horizontalAlignment: Text.AlignHCenter
                      width: parent.width
                      elide: Text.ElideRight
                    }
                    Label {
                      text: root.lastResult.metrics[modelData]
                      color: "#f1f5f9"
                      font.pixelSize: 16
                      font.bold: true
                      width: parent.width
                      horizontalAlignment: Text.AlignHCenter
                    }
                  }
                }
              }
            }

            Label {
              text: root.lastResult && root.lastResult.metrics && root.lastResult.metrics.summary
                    ? qsTr("检测到夹具 %1 个，颗粒 %2 个，刀路段 %3 个。")
                        .arg(root.lastResult.metrics.summary.fixtures ? root.lastResult.metrics.summary.fixtures.length : root.lastResult.metrics.fixture_count || 0)
                        .arg(root.lastResult.metrics.summary.particles ? root.lastResult.metrics.summary.particles.length : root.lastResult.metrics.particle_count || 0)
                        .arg(root.lastResult.metrics.toolpath_segments || 0)
                    : ""
              color: "#cbd5f5"
              wrapMode: Text.WordWrap
            }

            Label {
              text: root.lastResult && root.lastResult.capture
                    ? qsTr("采集: %1").arg(root.lastResult.capture.message || "")
                    : ""
              color: "#38bdf8"
              wrapMode: Text.WordWrap
            }

            ColumnLayout {
              Layout.fillWidth: true
              visible: root.lastResult && root.lastResult.visuals && Object.keys(root.lastResult.visuals).length > 0
              spacing: 4
              Label { text: qsTr("生成文件"); color: "#cbd5f5"; font.pixelSize: 16 }
              Repeater {
                model: root.lastResult ? Object.keys(root.lastResult.visuals || {}) : []
                delegate: ColumnLayout {
                  Layout.fillWidth: true
                  Label { text: modelData; color: "#94a3b8" }
                  Repeater {
                    model: root.lastResult.visuals[modelData]
                    delegate: Label {
                      text: "- " + modelData
                      color: "#f1f5f9"
                    }
                  }
                }
              }
            }
          }

          Label {
            visible: !root.lastResult
            text: qsTr("尚未运行任务，点击上方按钮开始。")
            color: "#94a3b8"
          }
        }
      }

      Rectangle {
        Layout.fillWidth: true
        radius: 10
        color: "#1e2432"
        border.color: "#2a3142"
        Layout.margins: 12

        ColumnLayout {
          anchors.fill: parent
          anchors.margins: 8
          Label { text: qsTr("标定工具"); font.pixelSize: 20; color: "#f8fafc"; Layout.margins: 8 }
          Flickable {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(720, root.height * 0.8)
            contentWidth: width
            contentHeight: calibrationCard.implicitHeight
            clip: true
            Calibration.CalibrationView {
              id: calibrationCard
              width: parent.width
            }
            ScrollBar.vertical: ScrollBar { }
          }
        }
      }

      Item { Layout.fillHeight: true }
    }

    ScrollBar.vertical: ScrollBar { }
  }

  FolderDialog {
    id: folderDialog
    title: qsTr("选择测试数据文件夹")
    onAccepted: root.folderPath = root.urlToPath(selectedFolder)
  }

  Component.onCompleted: loadDefaults()
}
