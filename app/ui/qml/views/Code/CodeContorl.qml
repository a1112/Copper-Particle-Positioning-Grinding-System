import QtQuick
import QtQuick.Controls.Material
import QtQuick.Layouts

import "../../components/btns" as Btns
import "../Base"
import "../../Api" as Api
import "../../cores" as Cores

RowLayout {
  Layout.fillWidth: true
  CodeFoot{
  }
  Item{
    Layout.fillWidth: true
  }

  Btns.ActionButton {
    id: btnRun
    text: '运行'
    onClicked: Api.ApiClient.startRun()
  }
  Btns.ActionButton {
    id: btnStop
    text: '停止'
    onClicked: Api.ApiClient.stopRun()
  }
  Btns.ActionButton {
    id: btnSave
    text: '保存'
    onClicked: { settings.savedText = editor.text; Cores.CoreError.showError('已保存到本地设置') }
  }
  Btns.ActionButton {
    id: btnRestore
    text: '恢复'
    onClicked: { if (settings.savedText) editor.text = settings.savedText }
  }
}
