import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../cores" as Cores

// Left-side history drawer
Drawer {
  id: historyDrawer
  edge: Qt.LeftEdge
  width: Math.min(420, parent ? parent.width * 0.4 : 420)
  height: parent ? parent.height : 600
  modal: false
  interactive: true
  focus: true
  dim: true

  property string idFilter: ""
  property string timeFilter: ""
  property var _filteredHistory: []

  function _formatTime(ts) {
    if (!ts)
      return ""
    try {
      var d = new Date(ts)
      return d.toLocaleString()
    } catch (e) {
      return ""
    }
  }

  function _matchFilter(entry) {
    if (!entry)
      return false
    var idText = ""
    var boardText = ""
    var statusText = ""
    if (entry.id !== undefined && entry.id !== null)
      idText = String(entry.id)
    if (entry.params && entry.params.code)
      boardText = String(entry.params.code)
    else if (entry.params && entry.params.board)
      boardText = String(entry.params.board)
    if (entry.metadata && entry.metadata.status)
      statusText = String(entry.metadata.status)

    if (idFilter && idFilter.length > 0) {
      if (idText.indexOf(idFilter) === -1 && boardText.indexOf(idFilter) === -1)
        return false
    }
    if (timeFilter && timeFilter.length > 0) {
      var timeText = _formatTime(entry.ts || 0)
      if (timeText.indexOf(timeFilter) === -1)
        return false
    }
    return true
  }

  function _rebuild() {
    var src = Cores.CoreCurrent && Cores.CoreCurrent.controlHistory
              ? Cores.CoreCurrent.controlHistory
              : []
    var result = []
    var limit = Cores.CoreCurrent ? Cores.CoreCurrent.historyLimit : 50
    for (var i = 0; i < src.length; ++i) {
      if (result.length >= limit)
        break
      var raw = src[i]
      if (!raw)
        continue
      var entry = {
        index: i + 1,
        id: raw.id !== undefined && raw.id !== null ? raw.id : (raw.metadata && raw.metadata.id !== undefined ? raw.metadata.id : (raw.params && raw.params.id !== undefined ? raw.params.id : i + 1)),
        params: raw.params || {},
        metadata: raw.metadata || {},
        ts: raw.ts || 0
      }
      if (_matchFilter(entry))
        result.push(entry)
    }
    _filteredHistory = result
  }

  onIdFilterChanged: _rebuild()
  onTimeFilterChanged: _rebuild()

  Component.onCompleted: _rebuild()

  Connections {
    target: Cores.CoreCurrent
    function onControlHistoryChanged() {
      historyDrawer._rebuild()
    }
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 12
    spacing: 10

    Label {
      text: qsTr("历史记录")
      font.bold: true
      font.pixelSize: 24
      Layout.alignment: Qt.AlignHCenter
    }

    RowLayout {
      spacing: 8
      Layout.fillWidth: true

      Label {
        text: qsTr("ID")
        Layout.preferredWidth: 30
      }
      TextField {
        Layout.fillWidth: true
        placeholderText: qsTr("按 ID / 板号 查询")
        text: historyDrawer.idFilter
        onTextChanged: historyDrawer.idFilter = text
      }
    }

    RowLayout {
      spacing: 8
      Layout.fillWidth: true

      Label {
        text: qsTr("时间")
        Layout.preferredWidth: 40
      }
      TextField {
        Layout.fillWidth: true
        placeholderText: qsTr("按时间关键字查询，例如 2025-01-08")
        text: historyDrawer.timeFilter
        onTextChanged: historyDrawer.timeFilter = text
      }
    }

    Rectangle {
      Layout.fillWidth: true
      height: 1
      color: Cores.CoreStyle.border
    }

    RowLayout {
      Layout.fillWidth: true
      spacing: 8

      Label {
        text: qsTr("ID")
        Layout.preferredWidth: 60
      }
      Label {
        text: qsTr("板号")
        Layout.fillWidth: true
      }
      Label {
        text: qsTr("时间")
        Layout.preferredWidth: 130
      }
      Label {
        text: qsTr("状态")
        Layout.preferredWidth: 70
      }
    }

    ListView {
      Layout.fillWidth: true
      Layout.fillHeight: true
      clip: true
      model: historyDrawer._filteredHistory

      delegate: Rectangle {
        width: ListView.view ? ListView.view.width : parent.width
        height: 28
        color: index % 2 === 0 ? "#111827" : "#0f172a"

        RowLayout {
          anchors.fill: parent
          anchors.margins: 4
          spacing: 8

          Label {
            text: modelData.id !== undefined && modelData.id !== null ? String(modelData.id) : String(modelData.index)
            Layout.preferredWidth: 60
            elide: Text.ElideRight
          }
          Label {
            text: modelData.params && modelData.params.code
                  ? String(modelData.params.code)
                  : (modelData.params && modelData.params.board
                     ? String(modelData.params.board)
                     : "")
            Layout.fillWidth: true
            elide: Text.ElideRight
          }
          Label {
            text: historyDrawer._formatTime(modelData.ts)
            Layout.preferredWidth: 130
            elide: Text.ElideRight
          }
          Label {
            text: modelData.metadata && modelData.metadata.status
                  ? String(modelData.metadata.status)
                  : ""
            Layout.preferredWidth: 70
            elide: Text.ElideRight
          }
        }
      }
    }

    RowLayout {
      Layout.fillWidth: true

      Label {
        text: qsTr("最多显示 %1 条").arg(Cores.CoreCurrent ? Cores.CoreCurrent.historyLimit : 50)
        color: Cores.CoreStyle.muted
      }
      Item { Layout.fillWidth: true }
      Button {
        text: qsTr("关闭")
        onClicked: historyDrawer.close()
      }
    }
  }
}

