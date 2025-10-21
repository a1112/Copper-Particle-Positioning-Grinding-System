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
    if (!lines || !lines.length)
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
  Column {
    id: contentColumn
    spacing: 10
    width: parent.width

    CodeViews.CodeHead {
      width: parent.width
      codeConnected: root.codeConnected
      runState: root.runState
      currentIndex: root.currentIndex
    }

    Item {
      width: parent.width
      Layout.fillWidth: true
      height: list.contentHeight>400?420:list.contentHeight+15

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

        delegate: Rectangle {
          readonly property bool isCurrent: index === Datas.CodeDatas.currentIndex
          readonly property bool isPast: index < Datas.CodeDatas.currentIndex
          width: list.width
          height: 32
          radius: 6
          color: isCurrent ? Qt.tint(Cores.CoreStyle.accent, "#22000000")
                  : (isPast ? Qt.tint(Cores.CoreStyle.success, "#15000000") : "transparent")
          border.width: isCurrent ? 1.2 : 0
          border.color: isCurrent ? Cores.CoreStyle.accent : "transparent"

          Behavior on color { ColorAnimation { duration: 150 } }
          Behavior on border.color { ColorAnimation { duration: 150 } }

          RowLayout {
            anchors.fill: parent
            anchors.margins: 8
            spacing: 10

            Rectangle {
              width: 36
              height: 22
              radius: 4
              color: isCurrent ? Cores.CoreStyle.accent :
                     (isPast ? Qt.tint(Cores.CoreStyle.success, "#33000000") : Cores.CoreStyle.surface)
              Label {
                anchors.centerIn: parent
                text: model.idx
                color: isCurrent ? "#000000" : Cores.CoreStyle.text
                font.family: "monospace"
              }
            }

            Label {
              Layout.fillWidth: true
              text: model.text
              color: Cores.CoreStyle.text
              font.family: "monospace"
              horizontalAlignment: Text.AlignLeft
              elide: Text.ElideRight
            }

            Label {
              text: model.status
              color: root.statusColor(model.status)
              font.bold: isCurrent
              Layout.preferredWidth: 78
              horizontalAlignment: Text.AlignHCenter
            }
          }
        }

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
