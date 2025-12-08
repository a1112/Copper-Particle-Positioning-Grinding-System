import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../../Api" as Api
import "../../../cores" as Cores
import "../../../datas" as Datas
import "../../../works" as Works
import "." as Layers
import ".." as ImageInfo

/* 二维图像视图
 * 展示加工区实时画面，并叠加夹具、刀具与坐标提示信息。
 */
Item {
  id: view
  Layout.fillWidth: true
  Layout.fillHeight: true

  property real imageWidth: 640
  property real imageHeight: 360
  property real pixelSizeMm: 0.2
  property var pathPoints: []
  property var toolWorldPosition: ({})
  property int fixtureColumns: 4
  property int fixtureRows: 4
  property real fixtureSizeMm: 8
  property real fixtureMarginMm: 6
  property var fixtures: []
  property var defectAreaRects: []
  property var defectSingleRects: []
  property var calibrationCore: Cores.CoreDataView
  property int recordId: Datas.TaskDatas.latestRecordId
  property var viewCore: ImageInfo.ViewCore{}


  readonly property real currentZoom: viewCore ? viewCore.zoom : 1.0
  readonly property point currentPanOffset: viewCore ? viewCore.panOffset : Qt.point(0, 0)
  readonly property bool simulateActive: viewCore ? viewCore.simulateActive : false
  readonly property int currentSimulateIndex: viewCore ? viewCore.simulateIndex : -1
  readonly property bool controlsEnabled: Datas.StatusDatas.forceEnableControls || Datas.StatusDatas.controlEnabled

  readonly property real fitScale: {
    if (imageWidth <= 0 || imageHeight <= 0 || width <= 0 || height <= 0)
      return 1
    var scaleW = width / imageWidth
    var scaleH = height / imageHeight
    var result = Math.min(scaleW, scaleH)
    return result > 0 ? result : 1
  }
  readonly property real displayWidth: imageWidth > 0 ? imageWidth * fitScale : 0
  readonly property real displayHeight: imageHeight > 0 ? imageHeight * fitScale : 0
  readonly property real scaleX: fitScale
  readonly property real scaleY: fitScale
  // 最近一次手动点检监控上下文
  property bool manualCheckActive: false
  property int manualCheckRecordId: 0
  property int manualCheckLastTaskId: 0
  property string manualCheckActionKey: "manual.check"
  property string manualCheckMessage: ""
  // 点检阈值（从设置界面读取）
  property real checkBaseline: 0.0
  property real checkAlarmRange: 0.5

  function _applyCheckSettings() {
    if (!Cores.CoreSettings)
      return
    var general = Cores.CoreSettings.parameterGeneral || {}
    var section = general.inspection || general.check || {}
    var b = Number(section.baseline)
    var r = Number(section.alarm_range)
    checkBaseline = isNaN(b) ? 0.0 : b
    checkAlarmRange = isNaN(r) ? 0.5 : r
  }

  function resetHover() {
    if (!viewCore)
      return
    viewCore.resetHover({
                          coordinateLayer: coordinateLayer,
                          clearCursor: function() { Cores.CoreDataView.clearCursor() }
                        })
  }

  function updateHover(localX, localY) {
    if (!viewCore)
      return
    viewCore.updateHover(localX, localY, {
                           scaleX: scaleX,
                           scaleY: scaleY,
                           imageWidth: imageWidth,
                           imageHeight: imageHeight,
                           pixelSizeMm: pixelSizeMm,
                           calibrationCore: calibrationCore,
                           coordinateLayer: coordinateLayer,
                           onHoverChanged: function(pixelPoint, worldPoint) {
                             Cores.CoreDataView.setCursor(pixelPoint, worldPoint, true)
                           }
                         })
  }

  function _corePanContext() {
    return {
      width: overlayArea ? overlayArea.width : width,
      height: overlayArea ? overlayArea.height : height,
      displayWidth: displayWidth,
      displayHeight: displayHeight,
      coordinateLayer: coordinateLayer,
      pathCanvas: pathCanvas,
      refreshHover: _refreshHover
    }
  }

  function _applyPanDelta(dx, dy) {
    if (!viewCore)
      return
    viewCore.applyPanDelta(dx, dy, _corePanContext())
  }

  function _updatePan(point) {
    if (!viewCore)
      return
    viewCore.updatePan(point, _corePanContext())
  }

  function _setZoom(targetZoom, focusPoint) {
    if (!viewCore)
      return
    viewCore.setZoom(targetZoom, focusPoint, _corePanContext())
  }

  function handleWheelZoom(wheel) {
    if (typeof contentGroup === "undefined")
      return
    var delta = wheel.angleDelta.y !== 0 ? wheel.angleDelta.y / 120 : wheel.pixelDelta.y / 120
    if (delta === 0)
      return
    var factor = Math.pow(1.2, delta)
    if (Math.abs(factor - 1) < 0.0001)
      return
    var localPoint = Qt.point(wheel.x, wheel.y)
    var mappedPoint = contentGroup.mapFromItem(overlayArea, localPoint)
    _setZoom(currentZoom * factor, mappedPoint)
    wheel.accepted = true
  }

  function _refreshHover() {
    if (typeof contentGroup === "undefined" || !viewCore || !viewCore.hoverValid)
      return
    var localX = viewCore.hoverPixel.x * scaleX
    var localY = viewCore.hoverPixel.y * scaleY
    if (!overlayArea || localX < 0 || localY < 0 || localX > overlayArea.width || localY > overlayArea.height) {
      resetHover()
      return
    }
    updateHover(localX, localY)
  }

  function _cloneParams(source) {
    if (!source || typeof source !== "object")
      return {}
    var copy = {}
    for (var key in source) {
      if (!source.hasOwnProperty(key))
        continue
      copy[key] = source[key]
    }
    return copy
  }

  function _buildControlParams(extraParams) {
    var params = _cloneParams(extraParams)
    var currentRecord = Cores.CoreCurrent.record && Cores.CoreCurrent.record.id ? Number(Cores.CoreCurrent.record.id) : 0
    if (currentRecord > 0)
      params.record_id = currentRecord
    else if (Datas.TaskDatas.readyRecordId && Datas.TaskDatas.readyRecordId > 0)
      params.record_id = Datas.TaskDatas.readyRecordId
    else if (Datas.TaskDatas.latestRecordId && Datas.TaskDatas.latestRecordId > 0)
      params.record_id = Datas.TaskDatas.latestRecordId

    var currentWorkpiece = Cores.CoreCurrent.workpiece && Cores.CoreCurrent.workpiece.id ? Number(Cores.CoreCurrent.workpiece.id) : 0
    if (currentWorkpiece > 0)
      params.workpiece_id = currentWorkpiece
    else if (Datas.TaskDatas.workpieceId && Datas.TaskDatas.workpieceId > 0)
      params.workpiece_id = Datas.TaskDatas.workpieceId

    params.manual = true
    return params
  }

  // 从标定夹具中提取点检区域（名称以 Check 开头）
  function _buildCheckRegions() {
    var regions = []
    var list = fixtures || []
    for (var i = 0; i < list.length; ++i) {
      var fixture = list[i]
      if (!fixture || !fixture.name)
        continue
      var name = String(fixture.name)
      if (name.indexOf("Check") !== 0 && name.indexOf("check") !== 0)
        continue
      var rect = null
      if (calibrationCore && calibrationCore.fixtureRectWorld !== undefined) {
        rect = calibrationCore.fixtureRectWorld(fixture)
      } else if (fixture.rect) {
        rect = fixture.rect
      }
      if (!rect)
        continue
      regions.push({
                     name: name,
                     rect: {
                       x: Number(rect.x || 0),
                       y: Number(rect.y || 0),
                       width: Number(rect.width || 0),
                       height: Number(rect.height || 0)
                     }
                   })
    }
    return regions
  }

  function triggerManualCheck() {
    if (!Datas.StatusDatas.forceEnableControls && !Datas.StatusDatas.controlEnabled)
      return
    var regions = _buildCheckRegions()
    if (!regions || regions.length === 0) {
      Cores.CoreError.showError(qsTr("未检测到点检区域，请检查标定标注"))
      return
    }
    var baseParams = _buildControlParams({})
    manualCheckRecordId = baseParams.record_id || 0
    manualCheckLastTaskId = 0
    manualCheckActive = true
    manualCheckMessage = ""
    var params = _cloneParams(baseParams)
    params.check_regions = regions
    Cores.CoreCurrent.pushControl(manualCheckActionKey, params, { source: "view2d_manual_check" })
    Api.ApiClient.control(manualCheckActionKey, params, function() {
      Works.TaskWork.refresh()
    }, function(_, errMessage) {
      console.warn("Manual check control action failed", errMessage)
      Cores.CoreError.showError(qsTr("手动点检下发失败: %1").arg(errMessage))
      Works.TaskWork.refresh()
    })
  }

  function _handleCheckResult(zValue, isAuto) {
    var baseline = checkBaseline
    var alarmRange = checkAlarmRange
    var diff = zValue - baseline
    var absDiff = Math.abs(diff)
    var ok = absDiff <= alarmRange
    var statusText = ok ? qsTr("成功") : qsTr("失败")
    var message = qsTr("点检值: %1\n点检基准: %2\n报警范围: %3\n差值: %4\n点检判断: %5")
        .arg(Number(zValue).toFixed(3))
        .arg(Number(baseline).toFixed(3))
        .arg(Number(alarmRange).toFixed(3))
        .arg(Number(diff).toFixed(3))
        .arg(statusText)
    if (ok) {
      Cores.CoreError.showError(message)
    } else {
      Cores.CoreError.showError(message)
    }
  }

  function dispatchContextControl(actionKey, extraParams) {
    if (!actionKey)
      return
    if (!Datas.StatusDatas.forceEnableControls && !Datas.StatusDatas.controlEnabled)
      return
    var params = _buildControlParams(extraParams)
    if (params.workpiece_id && params.workpiece_id > 0) {
      Cores.CoreCurrent.updateWorkpiece({
                                          id: params.workpiece_id,
                                          code: Datas.TaskDatas.workpieceCode,
                                          type: Datas.TaskDatas.workpieceType
                                        })
    }
    if (params.record_id && params.record_id > 0)
      Cores.CoreCurrent.updateRecord({ id: params.record_id })
    Cores.CoreCurrent.pushControl(actionKey, params, { source: "view2d_context_menu" })
    Api.ApiClient.control(actionKey, params, function() {
      Works.TaskWork.refresh()
    }, function(_, errMessage) {
      console.warn("View2D control action failed", actionKey, errMessage)
      Works.TaskWork.refresh()
    })
  }

  Menu {
    id: quickActionMenu
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

    MenuItem {
      text: qsTr("气缸全部夹紧")
      enabled: view.controlsEnabled
      onTriggered: view.dispatchContextControl("cylinder.clamp_all")
    }
    MenuItem {
      text: qsTr("气缸全部松开")
      enabled: view.controlsEnabled
      onTriggered: view.dispatchContextControl("cylinder.release_all")
    }
    MenuSeparator {}
    MenuItem {
      text: qsTr("主轴位置回零")
      enabled: view.controlsEnabled
      onTriggered: view.dispatchContextControl("motion.home")
    }
    MenuItem {
      text: qsTr("主轴Z值回零")
      enabled: view.controlsEnabled
      onTriggered: view.dispatchContextControl("spindle.home_z")
    }
    MenuItem {
      text: qsTr("主轴换刀")
      enabled: view.controlsEnabled
      onTriggered: view.dispatchContextControl("spindle.tool_change")
    }
    MenuItem {
      text: qsTr("主轴停止")
      enabled: view.controlsEnabled
      onTriggered: view.dispatchContextControl("spindle.stop")
    }
      MenuItem {
        text: qsTr("排屑打开")
        enabled: view.controlsEnabled
        onTriggered: view.dispatchContextControl("chip.open")
      }
      MenuItem {
        text: qsTr("排屑关闭")
        enabled: view.controlsEnabled
        onTriggered: view.dispatchContextControl("chip.close")
      }
      MenuItem {
        text: qsTr("气吹打开")
        enabled: view.controlsEnabled
        onTriggered: view.dispatchContextControl("air_blow.open")
      }
      MenuItem {
        text: qsTr("气吹关闭")
        enabled: view.controlsEnabled
        onTriggered: view.dispatchContextControl("air_blow.close")
      }
      MenuItem {
        text: qsTr("手动点检")
        enabled: view.controlsEnabled
        onTriggered: view.triggerManualCheck()
      }
  }

  function startSimulation() {
    if (!viewCore)
      return
    var started = viewCore.startSimulation(pathPoints)
    if (!started)
      return
    playbackTimer.start()
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
  }

  function stopSimulation() {
    if (!viewCore)
      return
    var changed = viewCore.stopSimulation()
    if (!changed)
      return
    playbackTimer.stop()
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
  }

  function toggleSimulation() {
    if (!viewCore)
      return
    var active = viewCore.toggleSimulation(pathPoints)
    if (active)
      playbackTimer.start()
    else
      playbackTimer.stop()
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
  }

  function _stepSimulation() {
    if (!viewCore)
      return
    var progressed = viewCore.stepSimulation(pathPoints)
    if (!progressed) {
      playbackTimer.stop()
      return
    }
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
  }

  Rectangle {
    anchors.fill: parent
    radius: 4
    color: Cores.CoreStyle.background
  }

  Timer {
    id: playbackTimer
    interval: Math.max(20, view.viewCore ? view.viewCore.simulateIntervalMs : 80)
    repeat: true
    running: view.simulateActive
    onTriggered: view._stepSimulation()
  }

  Item {
    id: viewport
    anchors.fill: parent
    clip: true
    Item {
      id: overlayArea
      width: view.displayWidth
      height: view.displayHeight
      anchors.centerIn: parent

      visible: captureImage.status === Image.Ready && width > 0 && height > 0
      Item {
        id: contentGroup
        width: overlayArea.width
        height: overlayArea.height
        // 不进行居中
        transform: [
          Scale {
            origin.x: overlayArea.width / 2
            origin.y: overlayArea.height / 2
            xScale: view.currentZoom
            yScale: view.currentZoom
          },
          Translate {
            x: view.currentPanOffset.x
            y: view.currentPanOffset.y
          }
        ]

        Layers.ImageLayer {
          id: captureImage
          anchors.fill: parent
          fillMode: Image.Stretch
          source: Cores.CoreState.current2dImageSource
          onPaintedSizeUpdated: {
            if (sourceSize && sourceSize.width > 0 && sourceSize.height > 0) {
              view.imageWidth = sourceSize.width
              view.imageHeight = sourceSize.height
              Datas.CalibrationData.imageWidth = sourceSize.width
              Datas.CalibrationData.imageHeight = sourceSize.height
            }
            view._updatePan(view.currentPanOffset)
            pathCanvas.requestPaint()
            coordinateLayer.requestUpdate()
            if (typeof cameraAxes !== "undefined")
              cameraAxes.requestUpdate()
          }
        }
        Layers.MaskLayer {
          id: particleMaskImage
          anchors.fill: parent
          fillMode: Image.Stretch
          source: Cores.CoreState.particleMaskSource
          maskOpacity: 0.7
          visibleMask: Cores.CoreState.showParticleMask
        }
        Canvas {
          id: pathCanvas
          anchors.fill: parent
          visible: Cores.CoreState.showPathOverlay
          onPaint: {
            if (!Cores.CoreState.showPathOverlay)
              return
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            var centerX = width / 2
            var centerY = height / 2
            var lenX = 16 * view.scaleX
            var lenY = 16 * view.scaleY
            ctx.strokeStyle = "#22d3ee"
            ctx.lineWidth = 1.2
            ctx.beginPath()
            ctx.moveTo(centerX - lenX, centerY)
            ctx.lineTo(centerX + lenX, centerY)
            ctx.moveTo(centerX, centerY - lenY)
            ctx.lineTo(centerX, centerY + lenY)
            ctx.stroke()

            var pts = view.pathPoints || []
            var count = Array.isArray(pts) ? pts.length : 0

            if (count >= 2) {
              var strokeColor = Cores.CoreCutting.runState === "RUNNING"
                  ? Cores.CoreStyle.accent
                  : Cores.CoreStyle.info
              ctx.strokeStyle = strokeColor
              ctx.lineWidth = 2
              ctx.beginPath()
              for (var i = 0; i < count; ++i) {
                var px = pts[i].x * view.scaleX
                var py = pts[i].y * view.scaleY
                if (i === 0)
                  ctx.moveTo(px, py)
                else
                  ctx.lineTo(px, py)
              }
              ctx.stroke()
            }

            if (count === 0)
              return

            ctx.lineWidth = 1
            ctx.font = "10px 'Monospace'"
            ctx.textAlign = "left"
            ctx.textBaseline = "top"

            for (var p = 0; p < count; ++p) {
              var point = pts[p]
              if (!point)
                continue
              var pointX = Number(point.x || 0) * view.scaleX
              var pointY = Number(point.y || 0) * view.scaleY
              var isStart = (p === 0)
              var isEnd = (p === count - 1)
              var baseColor = isStart ? "#10b981" : (isEnd ? "#ef4444" : "#0ea5e9")
              var radius = isStart || isEnd ? 4 : 3
              ctx.beginPath()
              ctx.fillStyle = baseColor
              ctx.strokeStyle = "rgba(14,116,144,0.55)"
              ctx.arc(pointX, pointY, radius, 0, Math.PI * 2)
              ctx.fill()
              ctx.stroke()

              if (point.def !== undefined && point.def !== null && point.def !== "") {
                ctx.fillStyle = Cores.CoreStyle.text
                ctx.fillText(String(point.def), pointX + 6, pointY - 6)
              }
            }

            if (view.currentSimulateIndex >= 0 && view.currentSimulateIndex < count) {
              var simPoint = pts[view.currentSimulateIndex]
              var simX = Number(simPoint.x || 0) * view.scaleX
              var simY = Number(simPoint.y || 0) * view.scaleY
              ctx.beginPath()
              ctx.fillStyle = "#f97316"
              ctx.strokeStyle = "#fb923c"
              ctx.lineWidth = 2
              ctx.arc(simX, simY, 6, 0, Math.PI * 2)
              ctx.fill()
              ctx.stroke()
            }
          }
          onWidthChanged: requestPaint()
          onHeightChanged: requestPaint()
          Component.onCompleted: requestPaint()
        }

        Layers.DefectOverlay {
          anchors.fill: parent
          areaRects: view.defectAreaRects
          singleRects: view.defectSingleRects
          scaleX: view.scaleX
          scaleY: view.scaleY
        }

        Layers.FixtureOverlay {
          anchors.fill: parent
          columns: view.fixtureColumns
          rows: view.fixtureRows
          imageWidth: view.imageWidth
          imageHeight: view.imageHeight
          pixelSizeMm: view.pixelSizeMm
          fixtureSizeMm: view.fixtureSizeMm
          fixtureMarginMm: view.fixtureMarginMm
          scaleX: view.scaleX
          scaleY: view.scaleY
          fixtures: view.fixtures
        }

        Layers.ToolOverlay {
          anchors.fill: parent
          toolWorldPosition: view.toolWorldPosition
          pixelSizeMm: view.pixelSizeMm
          imageWidth: view.imageWidth
          imageHeight: view.imageHeight
          scaleX: view.scaleX
          scaleY: view.scaleY
        }

        Layers.CameraAxesLayer {
          id: cameraAxes
          anchors.fill: parent
          z: -1
          enabled: view.viewCore ? view.viewCore.showCameraAxes : true
          viewItem: view
          calibrationCore: view.calibrationCore
          scaleX: view.scaleX
          scaleY: view.scaleY
          recordId: view.recordId
        }
        Layers.CoordinateOverlay {
          id: coordinateLayer
          anchors.fill: parent
          scaleX: view.scaleX
          scaleY: view.scaleY
          showLabel: false
        }
      }

      PinchHandler {
        id: pinchHandler
        target: null
        onActiveChanged: {
          if (active) {
            var minValue = view.viewCore ? view.viewCore.minZoom : 0.5
            var maxValue = view.viewCore ? view.viewCore.maxZoom : 4.0
            minimumScale = minValue / view.currentZoom
            maximumScale = maxValue / view.currentZoom
            if (view.viewCore) {
              view.viewCore.pinchStartZoom = view.currentZoom
              view.viewCore.pinchStartPan = view.currentPanOffset
            }
          } else {
            view._refreshHover()
          }
        }
        onScaleChanged: {
          var baseZoom = view.viewCore ? view.viewCore.pinchStartZoom : view.currentZoom
          var desired = baseZoom * scale
          var focus = contentGroup.mapFromItem(overlayArea, centroid.position)
          view._setZoom(desired, focus)
        }
        onTranslationChanged: {
          var basePan = view.viewCore ? view.viewCore.pinchStartPan : view.currentPanOffset
          var newPan = Qt.point(basePan.x + translation.x, basePan.y + translation.y)
          view._updatePan(newPan)
        }
      }

      onWidthChanged: Cores.CoreDataView.viewWidth = width
      onHeightChanged: Cores.CoreDataView.viewHeight = height
    }

    MouseArea {
      id: interactionArea
      anchors.fill: parent
      hoverEnabled: true
      acceptedButtons: Qt.LeftButton | Qt.RightButton
      cursorShape: (interactionArea.pressedButtons & Qt.LeftButton) ? Qt.ClosedHandCursor
                                                                   : (view.currentZoom > 1.0001 ? Qt.OpenHandCursor : Qt.ArrowCursor)

      onPressed: function(mouse) {
        if (mouse.button === Qt.RightButton) {
          if (quickActionMenu)
            quickActionMenu.popup(interactionArea, mouse.x, mouse.y)
          mouse.accepted = true
          return
        }
        if (mouse.button !== Qt.LeftButton)
          return
        if (view.viewCore)
          view.viewCore.dragLastPos = Qt.point(mouse.x, mouse.y)
      }

      onPositionChanged: function(mouse) {
        var localPoint = Qt.point(mouse.x, mouse.y)
        if ((interactionArea.pressedButtons & Qt.LeftButton) !== 0) {
          var lastPos = view.viewCore ? view.viewCore.dragLastPos : Qt.point(mouse.x, mouse.y)
          var dx = mouse.x - lastPos.x
          var dy = mouse.y - lastPos.y
          view._applyPanDelta(dx, dy)
          if (view.viewCore)
            view.viewCore.dragLastPos = localPoint
        }
        var mapped = contentGroup.mapFromItem(overlayArea, localPoint)
        view.updateHover(mapped.x, mapped.y)
      }

      onReleased: view._refreshHover()
      onCanceled: view._refreshHover()
      onExited: view.resetHover()

      onWheel: function(wheel) {
        handleWheelZoom(wheel)
      }
    }

  }

  // 手动点检任务状态监听
  Timer {
    id: manualCheckMonitor
    interval: 1000
    repeat: true
    running: view.manualCheckActive
    onTriggered: {
      var commands = Datas.TaskDatas.controlCommands || []
      var latestId = -1
      var latest = null
      for (var i = 0; i < commands.length; ++i) {
        var entry = commands[i]
        if (!entry)
          continue
        var key = entry.command_key || entry.commandKey || entry.command
        if (!key || String(key).toLowerCase() !== view.manualCheckActionKey)
          continue
        var recId = Number(entry.record_id || 0)
        if (view.manualCheckRecordId > 0 && recId !== view.manualCheckRecordId)
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
      view.manualCheckLastTaskId = latestId
      var statusRaw = latest.status
      if (statusRaw === undefined && latest.state !== undefined)
        statusRaw = latest.state
      var status = Number(statusRaw)
      if (status === 2) { // COMPLETED
        view.manualCheckActive = false
        var detail = latest.status_detail || latest.statusDetail || {}
        var params = detail.params || detail
        var zValue = params && params.z_value !== undefined ? Number(params.z_value) : NaN
        if (!isNaN(zValue)) {
          view._handleCheckResult(zValue, !!params.auto)
        } else {
          view.manualCheckMessage = qsTr("【%1】指令执行成功").arg(view.manualCheckActionKey)
          manualCheckMessageTimer.restart()
        }
      } else if (status === 3) { // FAILED
        view.manualCheckActive = false
        var detail = latest.status_detail || latest.statusDetail || {}
        var msg = ""
        if (detail && typeof detail === "object") {
          msg = detail.message || detail.detail || detail.error || ""
        }
        if (!msg && detail)
          msg = String(detail)
        if (!msg)
          msg = qsTr("点检执行失败，详见任务列表")
        Cores.CoreError.showError(qsTr("手动点检失败: %1").arg(msg))
      }
    }
  }

  Timer {
    id: manualCheckMessageTimer
    interval: 4000
    repeat: false
    onTriggered: view.manualCheckMessage = ""
  }

  Component.onCompleted: {
    _applyCheckSettings()
  }

  Rectangle {
    anchors.horizontalCenter: parent.horizontalCenter
    anchors.bottom: parent.bottom
    anchors.bottomMargin: 8
    radius: 6
    color: Qt.rgba(0.08, 0.08, 0.08, 0.8)
    visible: view.manualCheckMessage && view.manualCheckMessage.length > 0
    implicitWidth: msgLabel.implicitWidth + 24
    implicitHeight: msgLabel.implicitHeight + 12

    Label {
      id: msgLabel
      anchors.centerIn: parent
      color: "white"
      text: view.manualCheckMessage
    }
  }
  Layers.CoordinateInfo {
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.margins: 12
  }
  Button {
    id: simulateButton
    text: view.simulateActive ? qsTr("停止模拟") : qsTr("模拟路径")
    anchors.top: parent.top
    anchors.right: parent.right
    anchors.margins: 12
    visible: (view.pathPoints && view.pathPoints.length > 0)
    z: 100
    onClicked: view.toggleSimulation()
  }

  Connections {
    target: Cores.CoreSettings
    ignoreUnknownSignals: true
    function onParameterGeneralChanged() { view._applyCheckSettings() }
  }

  onPathPointsChanged: {
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
    var pts = pathPoints || []
    var count = Array.isArray(pts) ? pts.length : 0
    if (count === 0) {
      if (view.viewCore)
        view.viewCore.simulateIndex = -1
      if (simulateActive)
        stopSimulation()
    } else if (view.viewCore && view.viewCore.simulateIndex >= count) {
      view.viewCore.simulateIndex = count - 1
    }
  }
  onScaleXChanged: {
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
    if (typeof coordinateLayer !== "undefined")
      coordinateLayer.requestUpdate()
  }
  onScaleYChanged: {
    if (typeof pathCanvas !== "undefined")
      pathCanvas.requestPaint()
    if (typeof coordinateLayer !== "undefined")
      coordinateLayer.requestUpdate()
  }

  onWidthChanged: _updatePan(currentPanOffset)
  onHeightChanged: _updatePan(currentPanOffset)
  onDisplayWidthChanged: _updatePan(currentPanOffset)
  onDisplayHeightChanged: _updatePan(currentPanOffset)
  onCalibrationCoreChanged: {
    if (typeof cameraAxes !== "undefined")
      cameraAxes.requestUpdate()
  }
  onPixelSizeMmChanged: {
    if (typeof cameraAxes !== "undefined")
      cameraAxes.requestUpdate()
  }
  Connections {
    target: overlayArea
    function onWidthChanged() {
      if (typeof pathCanvas !== "undefined")
        pathCanvas.requestPaint()
    }
    function onHeightChanged() {
      if (typeof pathCanvas !== "undefined")
        pathCanvas.requestPaint()
    }
  }

  Connections {
    target: Cores.CoreState
    function onShowPathOverlayChanged() {
      if (typeof pathCanvas !== "undefined")
        pathCanvas.requestPaint()
      if (!Cores.CoreState.showPathOverlay && view.simulateActive)
        view.stopSimulation()
    }
    function onParticleMaskSourceChanged() { /* trigger overlay updates via binding */ }
  }

  Connections {
    target: viewCore
    ignoreUnknownSignals: true
    function onZoomChanged() {
      _updatePan(view.currentPanOffset)
      if (typeof pathCanvas !== "undefined")
        pathCanvas.requestPaint()
      if (typeof coordinateLayer !== "undefined")
        coordinateLayer.requestUpdate()
    }
    function onPanOffsetChanged() {
      if (typeof coordinateLayer !== "undefined")
        coordinateLayer.requestUpdate()
      if (typeof pathCanvas !== "undefined")
        pathCanvas.requestPaint()
      _refreshHover()
    }
    function onShowCameraAxesChanged() {
      if (typeof cameraAxes !== "undefined")
        cameraAxes.requestUpdate()
    }
  }

  Connections {
    target: calibrationCore
    ignoreUnknownSignals: true
    function onOriginXChanged() {
      if (typeof cameraAxes !== "undefined")
        cameraAxes.requestUpdate()
    }
    function onOriginYChanged() {
      if (typeof cameraAxes !== "undefined")
        cameraAxes.requestUpdate()
    }
    function onWorldWidthChanged() {
      if (typeof cameraAxes !== "undefined")
        cameraAxes.requestUpdate()
    }
    function onWorldHeightChanged() {
      if (typeof cameraAxes !== "undefined")
        cameraAxes.requestUpdate()
    }
    function onMachineMatrixChanged() {
      if (typeof cameraAxes !== "undefined")
        cameraAxes.requestUpdate()
    }
  }

  Connections {
    target: Datas.TaskDatas
    ignoreUnknownSignals: true
    function onLatestRecordIdChanged() {
      if (typeof cameraAxes !== "undefined")
        cameraAxes.requestUpdate()
      if (view.simulateActive)
        view.stopSimulation()
    }
  }
}
