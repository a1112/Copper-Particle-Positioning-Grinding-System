import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../../Api" as Api
import "../../components/btns" as Btns
import "../../works" as Works
import "." as CalibrationParts

ApplicationWindow {
  id: root
  visible: false
  width: 1280
  height: 760

  property var overview: ({ active: "", groups: [], globals: {} })
  property string currentGroup: ""
  property var detail: ({
    name: "",
    folder: "",
    record_id: null,
    points: [],
    matrices: {},
    image: ({ path: "", width: 0, height: 0 }),
    annotation: ""
  })
  property int selectedIndex: -1
  ListModel { id: pointsModel }
  property var editor: ({
    pixelX: "",
    pixelY: "",
    cameraX: "",
    cameraY: "",
    cameraZ: "",
    machineX: "",
    machineY: "",
    machineZ: ""
  })
  property string statusText: ""
  property bool statusIsError: false

  signal saved()

  function openDialog() {
    visible = true
    loadOverview()
  }

  function closeDialog() {
    visible = false
  }

  function syncPointsModel() {
    pointsModel.clear()
    var pts = detail.points || []
    for (var i = 0; i < pts.length; ++i)
      pointsModel.append({ item: pts[i] })
  }

  function loadOverview() {
    Api.ApiClient.calibrationList(function(payload) {
      overview = payload || { active: "", groups: [], globals: {} }
      if (overview.groups && overview.groups.length > 0) {
        var target = currentGroup || overview.active || overview.groups[0].name
        loadGroup(target)
      }
    }, function(status, message) {
      showMessage(qsTr("标定列表获取失败: %1").arg(message || status), true)
    })
  }

  function loadGroup(name) {
    if (!name)
      return
    Api.ApiClient.calibrationDetail(name, function(payload) {
      detail = payload || detail
      currentGroup = detail.name || name
      selectedIndex = -1
      syncPointsModel()
      clearEditor()
    }, function(status, message) {
      showMessage(qsTr("加载标定组失败: %1").arg(message || status), true)
    })
  }

  function setActive(name) {
    Api.ApiClient.calibrationActivate(name, function(payload) {
      detail = payload || detail
      currentGroup = detail.name
      loadOverview()
      syncPointsModel()
      showMessage(qsTr("已切换到标定组 %1").arg(currentGroup), false)
      if (Works.CalibrationWork && Works.CalibrationWork.refresh)
        Works.CalibrationWork.refresh()
    }, function(status, message) {
      showMessage(qsTr("切换标定组失败: %1").arg(message || status), true)
    })
  }

  function createGroup(nameText) {
    Api.ApiClient.calibrationCreate(nameText || "", null, function(payload) {
      detail = payload || detail
      currentGroup = detail.name
      loadOverview()
      syncPointsModel()
      showMessage(qsTr("已创建标定组 %1").arg(currentGroup), false)
      if (Works.CalibrationWork && Works.CalibrationWork.refresh)
        Works.CalibrationWork.refresh()
    }, function(status, message) {
      showMessage(qsTr("创建标定组失败: %1").arg(message || status), true)
    })
  }

  function deleteGroup(name) {
    Api.ApiClient.calibrationDelete(name, function(payload) {
      overview = payload || overview
      var next = overview && overview.groups && overview.groups.length > 0 ? overview.groups[0].name : ""
      currentGroup = next
      if (next)
        loadGroup(next)
      else
        detail = ({ points: [], matrices: {}, image: {}, annotation: "" })
      syncPointsModel()
      showMessage(qsTr("标定组已删除"), false)
    }, function(status, message) {
      showMessage(qsTr("删除标定组失败: %1").arg(message || status), true)
    })
  }

  function saveData() {
    if (!currentGroup)
      return
    var payload = {
      record_id: detail.record_id,
      points: detail.points || [],
      matrices: detail.matrices || {}
    }
    Api.ApiClient.calibrationSave(currentGroup, payload, function(resp) {
      detail = resp || detail
      statusText = qsTr("标定数据已保存")
      statusIsError = false
      saved()
      if (Works.CalibrationWork && Works.CalibrationWork.refresh)
        Works.CalibrationWork.refresh()
    }, function(status, message) {
      showMessage(qsTr("保存失败: %1").arg(message || status), true)
    })
  }

  function importCurrentImage() {
    if (!currentGroup)
      return
    Api.ApiClient.calibrationImportImage(currentGroup, "", true, function(payload) {
      detail = payload || detail
      showMessage(qsTr("已同步当前图像"), false)
    }, function(status, message) {
      showMessage(qsTr("导入图像失败: %1").arg(message || status), true)
    })
  }

  function importLocalImage(path) {
    if (!currentGroup || !path)
      return
    Api.ApiClient.calibrationImportImage(currentGroup, path, false, function(payload) {
      detail = payload || detail
      showMessage(qsTr("已导入本地图像"), false)
    }, function(status, message) {
      showMessage(qsTr("导入图像失败: %1").arg(message || status), true)
    })
  }

  function applyPixel(x, y) {
    editor.pixelX = x.toFixed(3)
    editor.pixelY = y.toFixed(3)
  }

  function clearEditor() {
    editor = {
      pixelX: "", pixelY: "",
      cameraX: "", cameraY: "", cameraZ: "",
      machineX: "", machineY: "", machineZ: ""
    }
  }

  function addPoint() {
    var pt = buildPointFromEditor()
    if (!pt)
      return
    detail.points = (detail.points || []).concat([pt])
    pointsModel.append({ item: pt })
    selectedIndex = detail.points.length - 1
    showMessage(qsTr("已添加点位"), false)
  }

  function computeMatrices() {
    if (!currentGroup)
      return
    Api.ApiClient.calibrationCompute(currentGroup, detail.points || [], function(resp) {
      var m = (resp && resp.matrices) || {}
      detail.matrices = m
      showMessage(qsTr("矩阵已计算"), false)
    }, function(status, message) {
      showMessage(qsTr("计算矩阵失败: %1").arg(message || status), true)
    })
  }

  function updatePoint() {
    if (selectedIndex < 0 || selectedIndex >= (detail.points || []).length)
      return
    var pt = buildPointFromEditor()
    if (!pt)
      return
    detail.points[selectedIndex] = pt
    detail.points = detail.points.slice()
    pointsModel.setProperty(selectedIndex, "item", pt)
    showMessage(qsTr("已更新点位"), false)
  }

  function removePoint() {
    if (selectedIndex < 0 || selectedIndex >= (detail.points || []).length)
      return
    detail.points.splice(selectedIndex, 1)
    detail.points = detail.points.slice()
    pointsModel.remove(selectedIndex, 1)
    selectedIndex = -1
    clearEditor()
    showMessage(qsTr("点位已删除"), false)
  }

  function buildPointFromEditor() {
    function num(val) {
      if (val === undefined || val === null)
        return null
      var n = Number(String(val).trim())
      return isNaN(n) ? null : n
    }
    var px = num(editor.pixelX)
    var py = num(editor.pixelY)
    if (px === null || py === null) {
      showMessage(qsTr("像素坐标不能为空"), true)
      return null
    }
    return {
      pixel: { x: px, y: py },
      camera: { x: num(editor.cameraX), y: num(editor.cameraY), z: num(editor.cameraZ) },
      machine: { x: num(editor.machineX), y: num(editor.machineY), z: num(editor.machineZ) }
    }
  }

  function loadPointToEditor(index) {
    if (index < 0 || index >= (detail.points || []).length)
      return
    var pt = detail.points[index]
    selectedIndex = index
    editor.pixelX = (pt.pixel && pt.pixel.x !== undefined) ? pt.pixel.x : ""
    editor.pixelY = (pt.pixel && pt.pixel.y !== undefined) ? pt.pixel.y : ""
    editor.cameraX = pt.camera && pt.camera.x !== undefined ? pt.camera.x : ""
    editor.cameraY = pt.camera && pt.camera.y !== undefined ? pt.camera.y : ""
    editor.cameraZ = pt.camera && pt.camera.z !== undefined ? pt.camera.z : ""
    editor.machineX = pt.machine && pt.machine.x !== undefined ? pt.machine.x : ""
    editor.machineY = pt.machine && pt.machine.y !== undefined ? pt.machine.y : ""
    editor.machineZ = pt.machine && pt.machine.z !== undefined ? pt.machine.z : ""
  }

  function showMessage(text, isError) {
    statusText = text || ""
    statusIsError = !!isError
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 5
    spacing: 5

    SplitView {
      Layout.fillHeight: true
      Layout.fillWidth: true
      spacing: 3

      CalibrationParts.CalibrationImagePane {
        id: imagePane
        SplitView.fillWidth: true
        SplitView.fillHeight: true
        currentImage: detail.image ? detail.image.path : ""
        points: detail.points || []
        selectedIndex: root.selectedIndex
        onPixelClicked: function(px, py) { root.applyPixel(px, py) }
        onImportCurrentRequested: root.importCurrentImage()
        onImportLocalRequested: function(path) { root.importLocalImage(path) }
      }

      ColumnLayout {
        SplitView.preferredWidth: 500
        SplitView.fillHeight: true
        spacing: 5

        CalibrationParts.CalibrationGroupPanel {
          SplitView.fillWidth: true
          Layout.fillWidth: true
          groups: overview.groups || []
          activeName: overview.active || ""
          onCreateRequested: function(name) { root.createGroup(name) }
          onActivateRequested: function(name) { root.setActive(name) }
          onDeleteRequested: function(name) { root.deleteGroup(name) }
          onRenameRequested: function(oldName, newName) {
            if (!oldName || !newName)
              return
            Api.ApiClient.calibrationRename(oldName, newName, function(payload) {
              detail = payload || detail
              currentGroup = detail.name
              loadOverview()
              syncPointsModel()
              showMessage(qsTr("分组已重命名为 %1").arg(currentGroup), false)
            }, function(status, message) {
              showMessage(qsTr("重命名失败: %1").arg(message || status), true)
            })
          }
          onOpenFolderRequested: function(name) {
            // 已在面板内直接用 Qt.openUrlExternally 打开，这里预留扩展
          }
        }

        CalibrationParts.CalibrationPointsPanel {
          Layout.fillWidth: true
          Layout.fillHeight: true
          pointsModel: pointsModel
          selectedIndex: root.selectedIndex
          editor: root.editor
          matrices: detail.matrices || {}
          onSelectRequested: function(idx) { root.loadPointToEditor(idx) }
          onAddRequested: root.addPoint()
          onUpdateRequested: root.updatePoint()
          onDeleteRequested: root.removePoint()
          onMatricesUpdated: function(m) { detail.matrices = m }
        }
      }
    }

    RowLayout {
      Layout.fillWidth: true
      spacing: 10
      Btns.ActionButton {
        text: qsTr("计算矩阵")
        enabled: (detail.points || []).length >= 3
        onClicked: computeMatrices()
      }
      Label {
        text: statusText
        color: statusIsError ? "#ef4444" : "#10b981"
        Layout.fillWidth: true
        wrapMode: Label.Wrap
      }
      Btns.ActionButton {
        text: qsTr("刷新")
        onClicked: loadOverview()
      }
      Btns.ActionButton {
        text: qsTr("保存")
        enabled: currentGroup.length > 0
        onClicked: saveData()
      }
      Btns.ActionButton {
        text: qsTr("关闭")
        onClicked: closeDialog()
      }
    }
  }
}
