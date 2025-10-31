import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base"
import "." as CodeViews
import "../../datas" as Datas
import "../../cores" as Cores

BaseCard {
  id: root
  signal requestBack()
  Layout.fillWidth: true
  readonly property bool programEmpty: codeModel.count === 0
  implicitHeight: contentColumn.implicitHeight + 16

  property ListModel codeModel: Datas.CodeDatas.model

  property int currentIndex: Datas.CodeDatas.currentIndex
  property string runState: Datas.CodeDatas.runState
  property bool codeConnected: Datas.CodeDatas.connected

  function statusColor(status) {
    switch (status) {
    case "RUNNING":
      return Cores.CoreStyle.accent
    case "OK":
      return Cores.CoreStyle.success
    case "FAIL":
    case "ERROR":
      return Cores.CoreStyle.danger
    default:
      return Cores.CoreStyle.muted
    }
  }

  function ensureCurrentVisible() {
    var cur = Datas.CodeDatas.currentIndex
    if (cur >= 0 && cur < codeModel.count)
      list.positionViewAtIndex(cur, ListView.Center)
  }

  function updateStatuses() {
    Datas.CodeDatas.updateStatuses()
    ensureCurrentVisible()
  }

  function syncCoreState() {
    Cores.CoreCutting.updateRunState(Datas.CodeDatas.runState, Datas.CodeDatas.currentIndex)
  }

  function refreshProgram() {
    var commands = Cores.CoreCutting.commands
    if (!Array.isArray(commands) || commands.length === 0) {
      var fallback = Datas.CodeDatas.lines
      if (!Array.isArray(fallback))
        fallback = []
      Datas.CodeDatas.setProgramList(fallback)
    } else {
      Datas.CodeDatas.setProgramList(commands)
    }
    updateStatuses()
  }


  ColumnLayout {
    id: contentColumn
    spacing: 10
    anchors.fill: parent
    CodeViews.CodeHead {
      width: parent.width
      codeConnected: root.codeConnected
      runState: root.runState
      currentIndex: root.currentIndex
      onBackRequested: root.requestBack()
    }

    Item {
      width: parent.width
      Layout.fillWidth: true
      Layout.fillHeight: true
      clip: true
      ListView {
        id: list
        anchors.fill: parent
        anchors.margins: 4
        model: codeModel
        clip: true
        focus: true
        delegate:CodeRunOneItem{}
        ScrollBar.vertical: ScrollBar { }
      }
    }
  }

  Component.onCompleted: {
    refreshProgram()
    syncCoreState()
  }

  Connections {
    target: Datas.CodeDatas

    function onCurrentIndexChanged() { syncCoreState(); updateStatuses() }
    function onRunStateChanged() { syncCoreState(); updateStatuses() }
  }

  Connections {
    target: Cores.CoreCutting
    function onCommandsChanged() { refreshProgram() }
    function onActiveIndexChanged() { updateStatuses() }
    function onSelectedIndexChanged() { updateStatuses() }
    function onRunStateChanged() { updateStatuses() }
  }
}
