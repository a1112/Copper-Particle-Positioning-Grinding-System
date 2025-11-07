import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../Control" as ControlViews
import "../../../components/Base" as BaseComponents
import "../../../cores" as Cores

ColumnLayout {
  visible: Cores.CoreState.isUseModel && Cores.CoreControl.allowDirectControl
  ControlViewHead{
    id:cvh
  }
  StackLayout {
    currentIndex: cvh.viewMode
    Layout.fillWidth: true
    Layout.fillHeight: true
    ControlViews.CylinderControl {

    }
    ControlViews.PTZControl {
      id: ptzControl

    }
  }
}
