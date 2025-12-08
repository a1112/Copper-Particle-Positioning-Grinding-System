import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQuick.Window
import "../../Api" as Api
import "../../components/btns" as Btns
import "../../works" as Works
import "." as CalibrationParts

ApplicationWindow {
  id: root
  visible: false
  width: Screen.width*0.7
  height: Screen.height*0.7
  title: "标定设置"
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
  property string statusText: ""
  property bool statusIsError: false

  // 点位列表模型，由 detail.points 同步构建
  ListModel { id: pointsModel }
  // 矩阵计数状态：-1=无任务, 0=已下发,1=计数中,2=完成,3=失败
  property int matrixCountStatus: -1

  function syncPointsModel() {
    pointsModel.clear()
    var pts = detail.points || []
    for (var i = 0; i < pts.length; ++i) {
      pointsModel.append({ item: pts[i] })
    }
  }

  signal saved()

  function openDialog() {
    visible = true
    loadOverview()
  }

  function closeDialog() {
    visible = false
  }

  function loadOverview() {
    Api.ApiClient.calibrationList(function(payload) {
      overview = payload || { active: "", groups: [], globals: {} }
      if (overview.groups && overview.groups.length > 0) {
        var target = currentGroup || overview.active || overview.groups[0].name
        loadGroup(target)
      }
      showMessage(qsTr("标定列表已刷新"), false)
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
      matrixCountActive = false
      matrixCountStatus = -1
      syncPointsModel()
    }, function(status, message) {
      showMessage(qsTr("加载标定组失败: %1").arg(message || status), true)
    })
  }

  function setActive(name) {
    Api.ApiClient.calibrationActivate(name, function(payload) {
      detail = payload || detail
      currentGroup = detail.name
      loadOverview()
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
    var pts = detail.points || []
    if (selectedIndex < 0 || selectedIndex >= pts.length) {
      showMessage(qsTr("请先在右侧选择一个点位"), true)
      return
    }
    var pt = pts[selectedIndex] || {}
    if (!pt.pixel)
      pt.pixel = { x: null, y: null }
    pt.pixel.x = Number(x.toFixed(3))
    pt.pixel.y = Number(y.toFixed(3))
    pts[selectedIndex] = pt
    detail.points = pts
    if (selectedIndex >= 0 && selectedIndex < pointsModel.count)
      pointsModel.setProperty(selectedIndex, "item", pt)
  }

  function addPoint() {
    var pt = {
      pixel: { x: 0, y: 0 },
      camera: { x: 0, y: 0, z: 0 },
      machine: { x: 0, y: 0, z: 0 }
    }
    var pts = detail.points || []
    pts = pts.concat([pt])
    detail.points = pts
    selectedIndex = detail.points.length - 1
    pointsModel.append({ item: pt })
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

  property bool matrixCountActive: false

  function startMatrixCountTask() {
    if (!currentGroup)
      return
    var pts = detail.points || []
    if (!pts || pts.length < 3) {
      showMessage(qsTr("矩阵计数至少需要 3 个点"), true)
      return
    }
    Api.ApiClient.post("/vision/calibrations/" + encodeURIComponent(currentGroup) + "/matrix-count",
      { points: pts },
      function(resp) {
        matrixCountActive = true
        matrixCountStatus = 0  // 0: 已下发
        showMessage(qsTr("矩阵计数任务已下发"), false)
      },
      function(status, message) {
        showMessage(qsTr("矩阵计数任务下发失败: %1").arg(message || status), true)
      }
    )
  }

  function updatePoint() {
    // 直接在 PintItem 中编辑 detail.points，这里仅做提示
    if (selectedIndex < 0 || selectedIndex >= (detail.points || []).length)
      return
    showMessage(qsTr("已更新点位"), false)
  }

  function removePoint() {
    if (selectedIndex < 0 || selectedIndex >= (detail.points || []).length)
      return
    var pts = detail.points || []
    pts.splice(selectedIndex, 1)
    detail.points = pts
    // 同步删除 ListModel 中对应条目
    if (selectedIndex >= 0 && selectedIndex < pointsModel.count)
      pointsModel.remove(selectedIndex, 1)
    selectedIndex = -1
    showMessage(qsTr("点位已删除"), false)
  }

  function buildPointFromEditor() {
    return null
  }

  function loadPointToEditor(index) {
    if (index < 0 || index >= (detail.points || []).length)
      return
    selectedIndex = index
  }

  function showMessage(text, isError) {
    statusText = text || ""
    statusIsError = !!isError
    if (!text)
      return
    resultPopup.message = text
    resultPopup.isError = !!isError
    resultPopup.open()
    resultPopupTimer.restart()
  }

  function pollMatrixCountStatus() {
    if (!matrixCountActive)
      return
    Api.ApiClient.get("/data/tasks/state",
      function(payload) {
        var commands = payload.control_commands || payload.command_list || []
        var latest = null
        var latestId = -1
        for (var i = 0; i < commands.length; ++i) {
          var entry = commands[i]
          if (!entry)
            continue
          var key = entry.command_key || entry.commandKey || entry.command
          if (!key || String(key).toLowerCase() !== "manual.matrix_count")
            continue
          var tid = Number(entry.id || entry.task_id || entry.taskId || 0)
          if (!isFinite(tid))
            tid = 0
          if (tid >= latestId) {
            latestId = tid
            latest = entry
          }
        }
        if (!latest)
          return
        var status = Number(latest.status)
        // 同步状态码到界面（0/1/2/3）
        matrixCountStatus = isNaN(status) ? -1 : status
        if (status === 0 || status === 1)
          return
        matrixCountActive = false
        var detailObj = latest.status_detail || latest.statusDetail || {}
        if (status === 3) {
          var msg = detailObj && (detailObj.message || detailObj.detail || detailObj.error) || ""
          if (!msg)
            msg = qsTr("矩阵计数失败，详见任务列表")
          showMessage(qsTr("矩阵计数失败: %1").arg(msg), true)
          return
        }
        if (status === 2) {
          matrixCountStatus = 2
          var params = detailObj.params || detailObj
          // 后端返回结构为 { matrix: [...] }
          var mat = params.matrix || params.camera_to_machine || params.cameraToMachine || null
          if (mat) {
            var m = detail.matrices || {}
            m.camera_to_machine = mat
            detail.matrices = m
          }
          showMessage(qsTr("矩阵计数完成"), false)
        }
      },
      function(status, message) {
        // 静默失败，等下次轮询
        console.log("pollMatrixCountStatus failed", status, message)
      }
    )
  }

  Popup {
    id: resultPopup

    modal: false
    focus: false
    padding: 16
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
    x: (root.width - width) / 2
    y: root.height - height - 32
    property string message: ""
    property bool isError: false
    background: Rectangle {
      color: resultPopup.isError ? "#7f1d1d" : "#064e3b"
      border.color: resultPopup.isError ? "#fca5a5" : "#6ee7b7"
      radius: 10
      opacity: 0.95
    }
    Column {
      spacing: 6

      Label {
        text: resultPopup.isError ? qsTr("操作失败") : qsTr("操作成功")
        font.bold: true
        color: "#f8fafc"
      }
      Label {
        text: resultPopup.message
        wrapMode: Label.Wrap
        color: "#f1f5f9"
      }
    }
    Timer {
      id: resultPopupTimer
      interval: 2600
      repeat: false
      running: false
      onTriggered: resultPopup.close()
    }
  }

  Timer {
    id: matrixCountTimer
    interval: 1000
    repeat: true
    running: matrixCountActive
    onTriggered: root.pollMatrixCountStatus()
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
        SplitView.preferredWidth: 800
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
          detailRef: detail
          selectedIndex: root.selectedIndex
          matrices: detail.matrices || {}
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
      Label {
        // 矩阵计数状态显示：0:已下发,1:计数中,2:计数完成,3:计数失败
        text: matrixCountStatus < 0
              ? ""
              : (matrixCountStatus === 0
                   ? qsTr("已下发")
                   : (matrixCountStatus === 1
                        ? qsTr("计数中")
                        : (matrixCountStatus === 2
                             ? qsTr("计数完成")
                             : qsTr("计数失败"))))
        color: matrixCountStatus === 3
               ? "#ef4444"
               : (matrixCountStatus === 2 ? "#10b981" : "#e5e7eb")
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        Layout.preferredWidth: 80
      }
      Btns.ActionButton {
        text: qsTr("矩阵计数")
        enabled: (detail.points || []).length >= 3 && !matrixCountActive
        onClicked: startMatrixCountTask()
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
