import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base"
import "../../cores" as Cores
import "../../datas" as Datas
import "../../Api" as Api
import "../ImageInfo/view2d" as View2D

BaseCard {
  id: root

  Layout.fillWidth: true
  Layout.fillHeight: true
  implicitHeight: contentLayout.implicitHeight + 32

  readonly property real _epsilon: 1e-9
  property bool cameraRequestActive: false
  property point requestedPixel: Qt.point(-1, -1)
  property string statusText: ""
  property bool statusIsError: false
  property string pixelMatrixText: ""
  property string cameraMatrixText: ""
  property string composedMatrixText: ""

  property bool currentPixelValid: false
  property real currentPixelX: 0
  property real currentPixelY: 0

  property bool currentCameraValid: false
  property real currentCameraX: 0
  property real currentCameraY: 0
  property real currentCameraZ: 0

  property bool currentMachineValid: false
  property real currentMachineX: 0
  property real currentMachineY: 0
  property real currentMachineZ: 0

  property real imageZoom: 1.0
  property real minImageZoom: 0.5
  property real maxImageZoom: 4.0

  ListModel {
    id: sampleModel
  }

  function showMessage(text, isError) {
    statusText = text || ""
    statusIsError = !!isError
  }

  function numberToText(value, decimals) {
    if (value === null || value === undefined)
      return ""
    if (!isFinite(value))
      return ""
    var precision = (decimals !== undefined) ? decimals : 4
    return Number(value).toFixed(precision)
  }

  function parseField(field) {
    if (!field || field.text === undefined)
      return null
    var trimmed = String(field.text).trim()
    if (trimmed.length === 0)
      return null
    var value = Number(trimmed)
    return isNaN(value) ? null : value
  }

  function setPixel(point) {
    if (!point)
      return
    currentPixelValid = true
    currentPixelX = Number(point.x)
    currentPixelY = Number(point.y)
    pixelXField.text = numberToText(currentPixelX, 3)
    pixelYField.text = numberToText(currentPixelY, 3)
  }

  function clearPixel() {
    currentPixelValid = false
    currentPixelX = 0
    currentPixelY = 0
    pixelXField.text = ""
    pixelYField.text = ""
  }

  function setCamera(vector, valid) {
    if (!vector || !valid) {
      currentCameraValid = false
      currentCameraX = 0
      currentCameraY = 0
      currentCameraZ = 0
      cameraXField.text = ""
      cameraYField.text = ""
      cameraZField.text = ""
      return
    }
    currentCameraValid = true
    currentCameraX = Number(vector.x)
    currentCameraY = Number(vector.y)
    currentCameraZ = Number(vector.z)
    cameraXField.text = numberToText(currentCameraX, 3)
    cameraYField.text = numberToText(currentCameraY, 3)
    cameraZField.text = numberToText(currentCameraZ, 3)
  }

  function setMachine(vector, valid) {
    if (!vector || !valid) {
      currentMachineValid = false
      currentMachineX = 0
      currentMachineY = 0
      currentMachineZ = 0
      machineXField.text = ""
      machineYField.text = ""
      machineZField.text = ""
      return
    }
    currentMachineValid = true
    currentMachineX = Number(vector.x)
    currentMachineY = Number(vector.y)
    currentMachineZ = Number(vector.z)
    machineXField.text = numberToText(currentMachineX, 3)
    machineYField.text = numberToText(currentMachineY, 3)
    machineZField.text = numberToText(currentMachineZ, 3)
  }

  function setImageZoom(targetZoom) {
    var minZ = minImageZoom
    var maxZ = maxImageZoom
    var z = Number(targetZoom)
    if (!isFinite(z) || z <= 0)
      z = 1.0
    if (z < minZ)
      z = minZ
    if (z > maxZ)
      z = maxZ
    if (Math.abs(z - imageZoom) < 0.0001)
      return
    imageZoom = z
  }

  function handleImageWheelZoom(wheel) {
    var delta = wheel.angleDelta && wheel.angleDelta.y !== 0
               ? wheel.angleDelta.y / 120
               : (wheel.pixelDelta ? wheel.pixelDelta.y / 120 : 0)
    if (delta === 0)
      return
    var factor = Math.pow(1.2, delta)
    if (Math.abs(factor - 1) < 0.0001)
      return
    setImageZoom(imageZoom * factor)
    wheel.accepted = true
  }

  function mapToPixel(localX, localY) {
    if (cameraImage.status !== Image.Ready)
      return null
    var paintedWidth = cameraImage.paintedWidth
    var paintedHeight = cameraImage.paintedHeight
    if (paintedWidth <= 0 || paintedHeight <= 0)
      return null
    var offsetX = (imageContainer.width - paintedWidth) / 2
    var offsetY = (imageContainer.height - paintedHeight) / 2
    var insideX = localX - offsetX
    var insideY = localY - offsetY
    if (insideX < 0 || insideY < 0 || insideX > paintedWidth || insideY > paintedHeight)
      return null
    var sourceWidth = cameraImage.sourceSize.width > 0 ? cameraImage.sourceSize.width : paintedWidth
    var sourceHeight = cameraImage.sourceSize.height > 0 ? cameraImage.sourceSize.height : paintedHeight
    var px = insideX * sourceWidth / paintedWidth
    var py = insideY * sourceHeight / paintedHeight
    return Qt.point(px, py)
  }

  function requestCameraSample(pixelPoint) {
    if (!pixelPoint)
      return
    cameraRequestActive = true
    requestedPixel = Qt.point(Math.round(pixelPoint.x), Math.round(pixelPoint.y))
    showMessage(qsTr("请求相机坐标中..."), false)
    var path = "/vision/pointcloud/pixel?x=" + requestedPixel.x + "&y=" + requestedPixel.y
    Api.ApiClient.get(path,
      function(payload) {
        cameraRequestActive = false
        if (payload && payload.camera) {
          var cam = payload.camera
          var vec = { x: Number(cam.x), y: Number(cam.y), z: Number(cam.z) }
          if (isFinite(vec.x) && isFinite(vec.y) && isFinite(vec.z)) {
            setCamera(vec, true)
            showMessage(qsTr("已获取相机坐标 (%1, %2, %3)").arg(numberToText(vec.x, 3)).arg(numberToText(vec.y, 3)).arg(numberToText(vec.z, 3)), false)
            return
          }
        }
        setCamera(null, false)
        showMessage(qsTr("相机返回数据无效"), true)
      },
      function(status, message) {
        cameraRequestActive = false
        setCamera(null, false)
        showMessage(qsTr("相机请求失败：%1 %2").arg(status).arg(message || ""), true)
      }
    )
  }

  function captureMachinePosition() {
    var payload = Datas.StatusDatas.lastMessage
    if (!payload || !payload.position) {
      showMessage(qsTr("当前无机床坐标数据"), true)
      return
    }
    var pos = payload.position
    var mx = Number(pos.x)
    var my = Number(pos.y)
    var mz = Number(pos.z)
    if (!isFinite(mx) || !isFinite(my) || !isFinite(mz)) {
      showMessage(qsTr("机床坐标格式无效"), true)
      return
    }
    setMachine({ x: mx, y: my, z: mz }, true)
    showMessage(qsTr("已载入机床坐标 (%1, %2, %3)").arg(numberToText(mx, 3)).arg(numberToText(my, 3)).arg(numberToText(mz, 3)), false)
  }

  function prepareCurrentSample() {
    var px = parseField(pixelXField)
    var py = parseField(pixelYField)
    var cx = parseField(cameraXField)
    var cy = parseField(cameraYField)
    var cz = parseField(cameraZField)
    var mx = parseField(machineXField)
    var my = parseField(machineYField)
    var mz = parseField(machineZField)
    if (px === null || py === null)
      return { ok: false, message: qsTr("请提供像素坐标") }
    if (cx === null || cy === null || cz === null)
      return { ok: false, message: qsTr("请提供相机坐标") }
    if (mx === null || my === null || mz === null)
      return { ok: false, message: qsTr("请提供机床坐标") }
    return {
      ok: true,
      sample: {
        pixelX: px,
        pixelY: py,
        cameraX: cx,
        cameraY: cy,
        cameraZ: cz,
        machineX: mx,
        machineY: my,
        machineZ: mz
      }
    }
  }

  function addSample() {
    var prepared = prepareCurrentSample()
    if (!prepared.ok) {
      showMessage(prepared.message, true)
      return
    }
    sampleModel.append(prepared.sample)
    showMessage(qsTr("已新增样本 #%1").arg(sampleModel.count), false)
  }

  function removeSample(index) {
    if (index < 0 || index >= sampleModel.count)
      return
    sampleModel.remove(index)
    showMessage(qsTr("已删除样本 #%1").arg(index + 1), false)
  }

  function clearSamples() {
    sampleModel.clear()
    showMessage(qsTr("已清空样本"), false)
    pixelMatrixText = ""
    cameraMatrixText = ""
    composedMatrixText = ""
  }

  function loadSample(index) {
    if (index < 0 || index >= sampleModel.count)
      return
    var entry = sampleModel.get(index)
    setPixel({ x: entry.pixelX, y: entry.pixelY })
    setCamera({ x: entry.cameraX, y: entry.cameraY, z: entry.cameraZ }, true)
    setMachine({ x: entry.machineX, y: entry.machineY, z: entry.machineZ }, true)
    showMessage(qsTr("已载入样本 #%1").arg(index + 1), false)
  }

  function toArray(model) {
    var list = []
    for (var i = 0; i < model.count; ++i)
      list.push(model.get(i))
    return list
  }

  function computeMatrices() {
    var samples = toArray(sampleModel)
    if (!samples.length) {
      showMessage(qsTr("请先采集样本"), true)
      return
    }
    var pixelResult = computePixelToCamera(samples)
    var cameraResult = computeCameraToMachine(samples)
    pixelMatrixText = pixelResult.text
    cameraMatrixText = cameraResult.text
    var composed = composePixelToMachine(pixelResult.matrix, cameraResult.matrix)
    composedMatrixText = composed.text
    var messages = []
    if (pixelResult.message)
      messages.push(pixelResult.message)
    if (cameraResult.message)
      messages.push(cameraResult.message)
    if (composed.message)
      messages.push(composed.message)
    showMessage(messages.join(" | "), pixelResult.error || cameraResult.error || composed.error)
  }

  function computePixelToCamera(samples) {
    var usable = []
    for (var i = 0; i < samples.length; ++i) {
      var s = samples[i]
      if (!isFinite(s.pixelX) || !isFinite(s.pixelY) ||
          !isFinite(s.cameraX) || !isFinite(s.cameraY) || !isFinite(s.cameraZ))
        continue
      usable.push(s)
    }
    if (usable.length < 3)
      return {
        matrix: null,
        text: qsTr("至少需要 3 个有效样本"),
        message: qsTr("像素->相机 样本不足"),
        error: true
      }
    var rows = []
    var targets = []
    for (i = 0; i < usable.length; ++i) {
      var u = usable[i]
      rows.push([u.pixelX, u.pixelY, 1, 0, 0, 0, 0, 0, 0])
      targets.push(u.cameraX)
      rows.push([0, 0, 0, u.pixelX, u.pixelY, 1, 0, 0, 0])
      targets.push(u.cameraY)
      rows.push([0, 0, 0, 0, 0, 0, u.pixelX, u.pixelY, 1])
      targets.push(u.cameraZ)
    }
    var params = solveLeastSquares(rows, targets, 9)
    if (!params)
      return {
        matrix: null,
        text: qsTr("像素->相机 求解失败"),
        message: qsTr("像素->相机 无法求解"),
        error: true
      }
    var matrix = [
      [params[0], params[1], params[2]],
      [params[3], params[4], params[5]],
      [params[6], params[7], params[8]]
    ]
    var rms = computePixelCameraRms(usable, matrix)
    var text = formatMatrix(matrix, 6)
    var message = qsTr("像素->相机 RMS: %1").arg(numberToText(rms, 4))
    return { matrix: matrix, text: text, message: message, error: false }
  }

  function computeCameraToMachine(samples) {
    var usable = []
    for (var i = 0; i < samples.length; ++i) {
      var s = samples[i]
      if (!isFinite(s.cameraX) || !isFinite(s.cameraY) || !isFinite(s.cameraZ) ||
          !isFinite(s.machineX) || !isFinite(s.machineY) || !isFinite(s.machineZ))
        continue
      usable.push(s)
    }
    if (usable.length < 4)
      return {
        matrix: null,
        text: qsTr("至少需要 4 个有效样本"),
        message: qsTr("相机->机床 样本不足"),
        error: true
      }
    var rows = []
    var targets = []
    for (i = 0; i < usable.length; ++i) {
      var u = usable[i]
      rows.push([u.cameraX, u.cameraY, u.cameraZ, 1, 0, 0, 0, 0, 0, 0, 0, 0])
      targets.push(u.machineX)
      rows.push([0, 0, 0, 0, u.cameraX, u.cameraY, u.cameraZ, 1, 0, 0, 0, 0])
      targets.push(u.machineY)
      rows.push([0, 0, 0, 0, 0, 0, 0, 0, u.cameraX, u.cameraY, u.cameraZ, 1])
      targets.push(u.machineZ)
    }
    var params = solveLeastSquares(rows, targets, 12)
    if (!params)
      return {
        matrix: null,
        text: qsTr("相机->机床 求解失败"),
        message: qsTr("相机->机床 无法求解"),
        error: true
      }
    var matrix = [
      [params[0], params[1], params[2], params[3]],
      [params[4], params[5], params[6], params[7]],
      [params[8], params[9], params[10], params[11]]
    ]
    var rms = computeCameraMachineRms(usable, matrix)
    var text = formatMatrix(matrix, 6)
    var message = qsTr("相机->机床 RMS: %1").arg(numberToText(rms, 4))
    return { matrix: matrix, text: text, message: message, error: false }
  }

  function composePixelToMachine(pixelMatrix, cameraMatrix) {
    if (!pixelMatrix || !cameraMatrix)
      return {
        matrix: null,
        text: qsTr("需先计算前两个矩阵"),
        message: qsTr("像素->机床 未生成"),
        error: true
      }
    var composed = [
      [0, 0, 0, cameraMatrix[0][3]],
      [0, 0, 0, cameraMatrix[1][3]],
      [0, 0, 0, cameraMatrix[2][3]]
    ]
    for (var row = 0; row < 3; ++row) {
      for (var col = 0; col < 3; ++col) {
        var sum = 0
        for (var k = 0; k < 3; ++k)
          sum += cameraMatrix[row][k] * pixelMatrix[k][col]
        composed[row][col] = sum
      }
    }
    var text = formatMatrix(composed, 6)
    return {
      matrix: composed,
      text: text,
      message: qsTr("像素->机床 矩阵生成完成"),
      error: false
    }
  }

  function computePixelCameraRms(samples, matrix) {
    if (!matrix)
      return 0
    var total = 0
    var count = 0
    for (var i = 0; i < samples.length; ++i) {
      var s = samples[i]
      var px = s.pixelX
      var py = s.pixelY
      var predictedX = matrix[0][0] * px + matrix[0][1] * py + matrix[0][2]
      var predictedY = matrix[1][0] * px + matrix[1][1] * py + matrix[1][2]
      var predictedZ = matrix[2][0] * px + matrix[2][1] * py + matrix[2][2]
      total += Math.pow(predictedX - s.cameraX, 2)
      total += Math.pow(predictedY - s.cameraY, 2)
      total += Math.pow(predictedZ - s.cameraZ, 2)
      count += 3
    }
    return Math.sqrt(total / Math.max(1, count))
  }

  function computeCameraMachineRms(samples, matrix) {
    if (!matrix)
      return 0
    var total = 0
    var count = 0
    for (var i = 0; i < samples.length; ++i) {
      var s = samples[i]
      var cx = s.cameraX
      var cy = s.cameraY
      var cz = s.cameraZ
      var predictedX = matrix[0][0] * cx + matrix[0][1] * cy + matrix[0][2] * cz + matrix[0][3]
      var predictedY = matrix[1][0] * cx + matrix[1][1] * cy + matrix[1][2] * cz + matrix[1][3]
      var predictedZ = matrix[2][0] * cx + matrix[2][1] * cy + matrix[2][2] * cz + matrix[2][3]
      total += Math.pow(predictedX - s.machineX, 2)
      total += Math.pow(predictedY - s.machineY, 2)
      total += Math.pow(predictedZ - s.machineZ, 2)
      count += 3
    }
    return Math.sqrt(total / Math.max(1, count))
  }

  function solveLeastSquares(rows, targets, unknowns) {
    if (!rows || !targets || rows.length !== targets.length)
      return null
    var n = unknowns
    var ata = []
    var atb = []
    for (var i = 0; i < n; ++i) {
      ata[i] = []
      for (var j = 0; j < n; ++j)
        ata[i][j] = 0
      atb[i] = 0
    }
    for (var rowIndex = 0; rowIndex < rows.length; ++rowIndex) {
      var row = rows[rowIndex]
      var target = targets[rowIndex]
      for (var a = 0; a < n; ++a) {
        var ra = row[a]
        atb[a] += ra * target
        for (var b = 0; b < n; ++b)
          ata[a][b] += ra * row[b]
      }
    }
    return solveLinearSystem(ata, atb)
  }

  function solveLinearSystem(matrix, vector) {
    if (!matrix || !vector)
      return null
    var n = matrix.length
    if (vector.length !== n)
      return null
    var aug = []
    for (var i = 0; i < n; ++i) {
      aug[i] = matrix[i].slice(0)
      aug[i].push(vector[i])
    }
    for (var col = 0; col < n; ++col) {
      var pivot = col
      var maxVal = Math.abs(aug[col][col])
      for (var row = col + 1; row < n; ++row) {
        var val = Math.abs(aug[row][col])
        if (val > maxVal) {
          maxVal = val
          pivot = row
        }
      }
      if (maxVal < _epsilon)
        return null
      if (pivot !== col) {
        var tmp = aug[pivot]
        aug[pivot] = aug[col]
        aug[col] = tmp
      }
      var pivotVal = aug[col][col]
      for (var j = col; j <= n; ++j)
        aug[col][j] /= pivotVal
      for (var row2 = 0; row2 < n; ++row2) {
        if (row2 === col)
          continue
        var factor = aug[row2][col]
        if (Math.abs(factor) < _epsilon)
          continue
        for (var j2 = col; j2 <= n; ++j2)
          aug[row2][j2] -= factor * aug[col][j2]
      }
    }
    var solution = []
    for (var k = 0; k < n; ++k)
      solution[k] = aug[k][n]
    return solution
  }

  function formatMatrix(matrix, decimals) {
    if (!matrix)
      return ""
    var lines = []
    for (var i = 0; i < matrix.length; ++i) {
      var row = matrix[i]
      var parts = []
      for (var j = 0; j < row.length; ++j)
        parts.push(numberToText(row[j], decimals !== undefined ? decimals : 6))
      lines.push(parts.join("  "))
    }
    return lines.join("\n")
  }

  function overlayPixelX() {
    if (!currentPixelValid)
      return -1000
    var width = overlay.width
    if (width <= 0)
      return -1000
    var sourceWidth = cameraImage.sourceSize.width > 0 ? cameraImage.sourceSize.width : width
    if (sourceWidth <= 0)
      return -1000
    return (currentPixelX / sourceWidth) * width
  }

  function overlayPixelY() {
    if (!currentPixelValid)
      return -1000
    var height = overlay.height
    if (height <= 0)
      return -1000
    var sourceHeight = cameraImage.sourceSize.height > 0 ? cameraImage.sourceSize.height : height
    if (sourceHeight <= 0)
      return -1000
    return (currentPixelY / sourceHeight) * height
  }

  ColumnLayout {
    id: contentLayout
    anchors.fill: parent
    anchors.margins: 12
    spacing: 10

    RowLayout {
      Layout.fillWidth: true
      spacing: 12

      Label {
        text: qsTr("标定采集")
        color: Cores.CoreStyle.text
        font.pixelSize: 20
        font.bold: true
      }

      Item { Layout.fillWidth: true }

      Label {
        text: qsTr("图像类型")
        color: Cores.CoreStyle.muted
      }

      ComboBox {
        id: imageTypeCombo
        Layout.preferredWidth: 120
        model: Cores.CoreUI.allImageType
        currentIndex: Cores.CoreState.current2DShowIndex
        onActivated: function(idx) {
          Cores.CoreState.current2DShowIndex = idx
          Cores.CoreState.refreshImageSource()
        }
      }

      Button {
        text: qsTr("刷新图像")
        enabled: !cameraRequestActive
        onClicked: Cores.CoreState.refreshImageSource()
      }
    }

    SplitView {
      Layout.fillWidth: true
      Layout.fillHeight: true

      Item {
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.preferredWidth: 640

        ColumnLayout {
          anchors.fill: parent
          spacing: 8

          Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 400
            radius: 6
            color: Cores.CoreStyle.background
            border.color: Cores.CoreStyle.border

            Item {
              id: imageContainer
              anchors.fill: parent
              clip: true

              Item {
                id: contentGroup
                anchors.fill: parent
                transform: Scale {
                  origin.x: contentGroup.width / 2
                  origin.y: contentGroup.height / 2
                  xScale: root.imageZoom
                  yScale: root.imageZoom
                }

                Image {
                  id: cameraImage
                  anchors.fill: parent
                  fillMode: Image.PreserveAspectFit
                  asynchronous: true
                  cache: false
                  source: Cores.CoreState.current2dImageSource
                }

                Item {
                  id: overlay
                  x: (imageContainer.width - cameraImage.paintedWidth) / 2
                  y: (imageContainer.height - cameraImage.paintedHeight) / 2
                  width: cameraImage.paintedWidth
                  height: cameraImage.paintedHeight
                  visible: width > 0 && height > 0 && cameraImage.status === Image.Ready

                  // 夹具与点检区域覆盖
                  View2D.FixtureOverlay {
                    anchors.fill: parent
                    imageWidth: Datas.CalibrationData.imageWidth > 0 ? Datas.CalibrationData.imageWidth : cameraImage.sourceSize.width
                    imageHeight: Datas.CalibrationData.imageHeight > 0 ? Datas.CalibrationData.imageHeight : cameraImage.sourceSize.height
                    pixelSizeMm: (Datas.CalibrationData.worldWidth > 0 && Datas.CalibrationData.imageWidth > 0)
                                 ? Datas.CalibrationData.worldWidth / Datas.CalibrationData.imageWidth
                                 : 0.2
                    scaleX: cameraImage.paintedWidth > 0 && imageWidth > 0 ? cameraImage.paintedWidth / imageWidth : 1.0
                    scaleY: cameraImage.paintedHeight > 0 && imageHeight > 0 ? cameraImage.paintedHeight / imageHeight : 1.0
                    fixtures: Datas.CalibrationData.fixtures
                  }

                  Rectangle {
                    width: 1
                    height: parent.height
                    color: Cores.CoreStyle.muted
                    opacity: 0.35
                    visible: root.currentPixelValid
                    x: Math.max(-width, root.overlayPixelX())
                  }

                  Rectangle {
                    width: parent.width
                    height: 1
                    color: Cores.CoreStyle.muted
                    opacity: 0.35
                    visible: root.currentPixelValid
                    y: Math.max(-height, root.overlayPixelY())
                  }

                  Rectangle {
                    width: 14
                    height: 14
                    radius: 7
                    border.width: 2
                    border.color: Cores.CoreStyle.accent
                    color: "#00000000"
                    visible: root.currentPixelValid
                    x: root.overlayPixelX() - width / 2
                    y: root.overlayPixelY() - height / 2
                  }
                }
              }

              MouseArea {
                anchors.fill: parent
                enabled: cameraImage.status === Image.Ready
                hoverEnabled: true
                cursorShape: Qt.CrossCursor
                onClicked: function(mouse) {
                  var localPoint = Qt.point(mouse.x, mouse.y)
                  var mappedPoint = contentGroup.mapFromItem(imageContainer, localPoint)
                  var pixel = root.mapToPixel(mappedPoint.x, mappedPoint.y)
                  if (!pixel) {
                    showMessage(qsTr("请点击有效图像区域"), true)
                    return
                  }
                  setPixel(pixel)
                  showMessage(qsTr("已选择像素 (%1, %2)").arg(numberToText(pixel.x, 2)).arg(numberToText(pixel.y, 2)), false)
                  requestCameraSample(pixel)
                }
                onWheel: function(wheel) {
                  root.handleImageWheelZoom(wheel)
                }
              }
            }
          }

          Label {
            Layout.fillWidth: true
            text: statusText
            wrapMode: Text.WordWrap
            color: statusIsError ? Cores.CoreStyle.danger : Cores.CoreStyle.muted
          }
        }
      }

      ColumnLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true
        spacing: 10

        GroupBox {
          title: qsTr("当前采样")
          Layout.fillWidth: true

          ColumnLayout {
            Layout.fillWidth: true
            spacing: 6

            GridLayout {
              Layout.fillWidth: true
              columns: 6
              columnSpacing: 6
              rowSpacing: 4

              Label { text: qsTr("像素 X"); color: Cores.CoreStyle.muted }
              TextField {
                id: pixelXField
                Layout.preferredWidth: 90
                inputMethodHints: Qt.ImhFormattedNumbersOnly
              }
              Label { text: qsTr("像素 Y"); color: Cores.CoreStyle.muted }
              TextField {
                id: pixelYField
                Layout.preferredWidth: 90
                inputMethodHints: Qt.ImhFormattedNumbersOnly
              }
              Item { Layout.fillWidth: true }
              Item { Layout.fillWidth: true }

              Label { text: qsTr("相机 X"); color: Cores.CoreStyle.muted }
              TextField {
                id: cameraXField
                Layout.preferredWidth: 90
                inputMethodHints: Qt.ImhFormattedNumbersOnly
              }
              Label { text: qsTr("相机 Y"); color: Cores.CoreStyle.muted }
              TextField {
                id: cameraYField
                Layout.preferredWidth: 90
                inputMethodHints: Qt.ImhFormattedNumbersOnly
              }
              Label { text: qsTr("相机 Z"); color: Cores.CoreStyle.muted }
              TextField {
                id: cameraZField
                Layout.preferredWidth: 90
                inputMethodHints: Qt.ImhFormattedNumbersOnly
              }

              Label { text: qsTr("机床 X"); color: Cores.CoreStyle.muted }
              TextField {
                id: machineXField
                Layout.preferredWidth: 90
                inputMethodHints: Qt.ImhFormattedNumbersOnly
              }
              Label { text: qsTr("机床 Y"); color: Cores.CoreStyle.muted }
              TextField {
                id: machineYField
                Layout.preferredWidth: 90
                inputMethodHints: Qt.ImhFormattedNumbersOnly
              }
              Label { text: qsTr("机床 Z"); color: Cores.CoreStyle.muted }
              TextField {
                id: machineZField
                Layout.preferredWidth: 90
                inputMethodHints: Qt.ImhFormattedNumbersOnly
              }
            }

            RowLayout {
              Layout.fillWidth: true
              spacing: 8

              Button {
                text: qsTr("读取机床坐标")
                onClicked: captureMachinePosition()
              }

              Item { Layout.fillWidth: true }

              Button {
                text: qsTr("添加样本")
                onClicked: addSample()
              }
              Button {
                text: qsTr("清空样本")
                enabled: sampleModel.count > 0
                onClicked: clearSamples()
              }
            }
          }
        }

        GroupBox {
          title: qsTr("样本列表")
          Layout.fillWidth: true
          Layout.fillHeight: true

          ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 4

            RowLayout {
              Layout.fillWidth: true
              spacing: 6

              Label { text: qsTr("#"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 24 }
              Label { text: qsTr("像素 (x, y)"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 120 }
              Label { text: qsTr("相机 (x, y, z)"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 170 }
              Label { text: qsTr("机床 (x, y, z)"); color: Cores.CoreStyle.muted; Layout.preferredWidth: 170 }
              Item { Layout.fillWidth: true }
            }

            Rectangle {
              Layout.fillWidth: true
              Layout.fillHeight: true
              radius: 4
              color: "#00000020"
              border.color: Cores.CoreStyle.border

              ListView {
                id: sampleList
                anchors.fill: parent
                clip: true
                model: sampleModel

                delegate: Rectangle {
                  width: parent.width
                  height: 36
                  color: ListView.isCurrentItem ? "#FFFFFF10" : "transparent"
                  border.color: "#FFFFFF20"
                  border.width: 0

                  RowLayout {
                    anchors.fill: parent
                    anchors.margins: 6
                    spacing: 6

                    Label {
                      text: index + 1
                      color: Cores.CoreStyle.text
                      Layout.preferredWidth: 24
                    }
                    Label {
                      text: numberToText(pixelX, 2) + ", " + numberToText(pixelY, 2)
                      color: Cores.CoreStyle.text
                      Layout.preferredWidth: 120
                    }
                    Label {
                      text: numberToText(cameraX, 2) + ", " + numberToText(cameraY, 2) + ", " + numberToText(cameraZ, 2)
                      color: Cores.CoreStyle.text
                      Layout.preferredWidth: 170
                    }
                    Label {
                      text: numberToText(machineX, 2) + ", " + numberToText(machineY, 2) + ", " + numberToText(machineZ, 2)
                      color: Cores.CoreStyle.text
                      Layout.preferredWidth: 170
                    }

                    Item { Layout.fillWidth: true }

                    Button {
                      text: qsTr("载入")
                      onClicked: loadSample(index)
                    }

                    Button {
                      text: qsTr("删除")
                      onClicked: removeSample(index)
                    }
                  }
                }
              }
            }
          }
        }

        GroupBox {
          title: qsTr("转换矩阵")
          Layout.fillWidth: true

          ColumnLayout {
            Layout.fillWidth: true
            spacing: 6

            Button {
              text: qsTr("计算转换矩阵")
              enabled: sampleModel.count >= 3
              onClicked: computeMatrices()
            }

            Label { text: qsTr("像素 -> 相机"); color: Cores.CoreStyle.muted }
            TextArea {
              Layout.fillWidth: true
              Layout.preferredHeight: 80
              text: pixelMatrixText
              readOnly: true
              wrapMode: TextEdit.NoWrap
              font.family: "Consolas"
              background: Rectangle { color: "#00000020"; radius: 4 }
            }

            Label { text: qsTr("相机 -> 机床"); color: Cores.CoreStyle.muted }
            TextArea {
              Layout.fillWidth: true
              Layout.preferredHeight: 80
              text: cameraMatrixText
              readOnly: true
              wrapMode: TextEdit.NoWrap
              font.family: "Consolas"
              background: Rectangle { color: "#00000020"; radius: 4 }
            }

            Label { text: qsTr("像素 -> 机床"); color: Cores.CoreStyle.muted }
            TextArea {
              Layout.fillWidth: true
              Layout.preferredHeight: 80
              text: composedMatrixText
              readOnly: true
              wrapMode: TextEdit.NoWrap
              font.family: "Consolas"
              background: Rectangle { color: "#00000020"; radius: 4 }
            }
          }
        }
      }
    }
  }
}
