import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../../cores" as Cores
import "../../components/btns" as Btns
Item {
  id: root
  property url currentImage: ""
  property var points: []
  property int selectedIndex: -1
  property point cursorPixel: Qt.point(-1, -1)
  property point mappedWorld: Qt.point(0, 0)

  signal pixelClicked(real x, real y)
  signal importCurrentRequested()
  signal importLocalRequested(string path)

  function _sourceWidth() { return image.sourceSize && image.sourceSize.width > 0 ? image.sourceSize.width : image.implicitWidth }
  function _sourceHeight() { return image.sourceSize && image.sourceSize.height > 0 ? image.sourceSize.height : image.implicitHeight }

  function _mapMouseToImage(mx, my) {
    var paintedW = image.paintedWidth
    var paintedH = image.paintedHeight
    if (paintedW <= 0 || paintedH <= 0)
      return Qt.point(-1, -1)
    var offsetX = (image.width - paintedW) / 2
    var offsetY = (image.height - paintedH) / 2
    var sx = _sourceWidth() / paintedW
    var sy = _sourceHeight() / paintedH
    var px = (mx - offsetX) * sx
    var py = (my - offsetY) * sy
    var clampedX = Math.max(0, Math.min(px, _sourceWidth()))
    var clampedY = Math.max(0, Math.min(py, _sourceHeight()))
    return Qt.point(clampedX, clampedY)
  }

  function _mapImageToView(px, py) {
    var paintedW = image.paintedWidth
    var paintedH = image.paintedHeight
    if (paintedW <= 0 || paintedH <= 0)
      return Qt.point(-1000, -1000)
    var offsetX = (image.width - paintedW) / 2
    var offsetY = (image.height - paintedH) / 2
    var sx = paintedW / Math.max(_sourceWidth(), 1)
    var sy = paintedH / Math.max(_sourceHeight(), 1)
    return Qt.point(offsetX + px * sx, offsetY + py * sy)
  }

  ColumnLayout {
    anchors.fill: parent
    spacing: 6

    RowLayout {
      Layout.fillWidth: true

      Btns.ActionButton {
        text: qsTr("导入本地图像")
        onClicked: fileDialog.open()
      }
      Btns.ActionButton {
        text: qsTr("使用当前图像")
        onClicked: root.importCurrentRequested()
      }
      Item { Layout.fillWidth: true }
      Label {
        text: qsTr("像素: %1, %2  世界: %3, %4")
              .arg(cursorPixel.x.toFixed(1)).arg(cursorPixel.y.toFixed(1))
              .arg(mappedWorld.x.toFixed(2)).arg(mappedWorld.y.toFixed(2))
        color: "#e5e7eb"
        horizontalAlignment: Text.AlignRight
        Layout.fillWidth: true
      }
    }

    Rectangle {
      Layout.fillWidth: true
      Layout.fillHeight: true
      color: "#0f172a"
      radius: 6
      border.color: "#1e293b"
      clip: true

      Image {
        id: image
        anchors.fill: parent
        fillMode: Image.PreserveAspectFit
        source: root.currentImage
      }

      MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onPositionChanged: {
          var pt = root._mapMouseToImage(mouse.x, mouse.y)
          root.cursorPixel = pt
          var w = Cores.CoreDataView.imageToWorld(pt)
          root.mappedWorld = Qt.point(Number(w.x || 0), Number(w.y || 0))
        }
        onClicked: {
          var pt = root._mapMouseToImage(mouse.x, mouse.y)
          root.pixelClicked(pt.x, pt.y)
        }
      }

      Repeater {
        model: root.points
        delegate: Rectangle {
          required property int index
          required property var modelData
          width: index === root.selectedIndex ? 16 : 12
          height: width
          radius: width / 2
          color: index === root.selectedIndex ? "#10b981" : "#38bdf8"
          border.color: "#0f172a"
          visible: modelData && modelData.pixel !== undefined
          x: root._mapImageToView(modelData.pixel.x || 0, modelData.pixel.y || 0).x - width / 2
          y: root._mapImageToView(modelData.pixel.x || 0, modelData.pixel.y || 0).y - height / 2
        }
      }
    }
  }

  FileDialog {
    id: fileDialog
    title: qsTr("选择图像文件")
    fileMode: FileDialog.OpenFile
    nameFilters: [qsTr("图像 (*.png *.tif *.tiff *.jpg *.jpeg)")]
    onAccepted: {
      if (selectedFile && selectedFile.length > 0)
        root.importLocalRequested(selectedFile)
    }
  }
}
