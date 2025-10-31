import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../Control" as ControlViews
import "../../../components/Base" as BaseComponents
ColumnLayout {
  ControlViewHead{

  }
 StackLayout {
      Layout.fillWidth: true
      Layout.fillHeight: true
      ControlViews.PTZControl {
        id: ptzControl
        Layout.fillWidth: true
        Layout.preferredHeight: 240
      }
      ControlViews.CylinderControl {
        Layout.fillWidth: true
        Layout.preferredHeight: 220
      }
    }
}
