import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../../components/Base"
import "../../../cores" as Cores

Row {
  spacing: 8

  CheckDelegateBase {
    text: qsTr("粒子")
    checked: Cores.CoreState.showParticleMask
    onToggled: Cores.CoreState.showParticleMask = checked
  }

  CheckDelegateBase {
    text: qsTr("路径")
    checked: Cores.CoreState.showPathOverlay
    onToggled: Cores.CoreState.showPathOverlay = checked
  }

  CheckDelegateBase {
    text: qsTr("原图")
    visible: false
    checked: Cores.CoreState.showOriginalSource
    onToggled: Cores.CoreState.showOriginalSource = checked
  }
}
