import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base"
import "." as CodeViews
import "../../datas" as Datas
import "../../cores" as Cores

BaseCard {
  id: root
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
      codeModel.append({
        idx: i + 1,
        text: String(lines[i]),
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

  function refreshProgram() {
    var lines = Datas.CodeDatas.lines
    if (!Array.isArray(lines))
      lines = []
    setProgram(lines)
  }
  height: contentColumn.height


  ColumnLayout {
    id: contentColumn
    spacing: 10
    anchors.fill: parent
    CodeViews.CodeHead {
      width: parent.width
      codeConnected: root.codeConnected
      runState: root.runState
      currentIndex: root.currentIndex
    }

    Item {
      width: parent.width
      Layout.fillWidth: true
      Layout.fillHeight: true
      // height: list.contentHeight>400?420:list.contentHeight+15

      clip: true
      Frame{
        anchors.fill: parent
      }
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

      Label {
        anchors.centerIn: parent
        color: Cores.CoreStyle.muted
        visible: root.programEmpty
        wrapMode: Text.WordWrap
        horizontalAlignment: Text.AlignHCenter
      }
    }
  }

  Component.onCompleted: refreshProgram()

  Connections {
    target: Datas.CodeDatas

    function onLinesChanged() { refreshProgram() }
    function onCurrentIndexChanged() { updateStatuses() }
    function onRunStateChanged() { updateStatuses() }
  }
}
