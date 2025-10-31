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

  ListModel { id: codeModel }

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

  function setProgram(lines) {
    codeModel.clear()
    if (!Array.isArray(lines))
      return
    if (lines.length === 0)
      return
    for (var i = 0; i < lines.length; ++i) {
      var entry = lines[i]
      var displayText
      if (entry === undefined || entry === null) {
        displayText = "-"
      } else if (typeof entry === "object") {
        var text = ""
        if (entry.displayText !== undefined)
          text = entry.displayText
        else if (entry.text !== undefined)
          text = entry.text
        else if (entry.command !== undefined)
          text = entry.command
        else
          text = String(entry)
        displayText = String(text)
      } else {
        displayText = String(entry)
      }
      codeModel.append({
        idx: i + 1,
        text: displayText,
        status: "READY"
      })
    }
    updateStatuses()
  }

  function ensureCurrentVisible() {
    var cur = Datas.CodeDatas.currentIndex
    if (cur >= 0 && cur < codeModel.count)
      list.positionViewAtIndex(cur, ListView.Center)
  }

  function updateStatuses() {
    var cur = Datas.CodeDatas.currentIndex
    for (var i = 0; i < codeModel.count; ++i) {
      var status = "READY"
      if (i === cur)
        status = Datas.CodeDatas.runState === "ERROR" ? "FAIL" : "RUNNING"
      else if (i < cur)
        status = "OK"
      codeModel.setProperty(i, "status", status)
    }
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
      setProgram(fallback)
    } else {
      setProgram(commands)
    }
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

    function onLinesChanged() { refreshProgram() }
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
