import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../views/Calibration" as Calibration

Item {
  id: root
  Layout.fillWidth: true
  Layout.fillHeight: true

  Flickable {
    id: scrollArea
    anchors.fill: parent
    contentWidth: width
    contentHeight: calibrationCard.implicitHeight
    clip: true

    Calibration.CalibrationView {
      id: calibrationCard
      width: scrollArea.width
    }

    ScrollBar.vertical: ScrollBar { }
  }
}
