import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../datas" as Datas
import "../Base"
import "../../cores" as Cores

/* 日志视图卡片
 * 负责展示 WebSocket 推送的日志信息，可按等级筛选并选择是否自动滚动。
 */
BaseCard {
  id: root

  property bool autoScroll: true
  property int maxRows: 1000
  property real preservedBottomOffset: 0

  // 将后端传来的字符串中 ``n`` 转换为真实换行，方便阅读。
  function normalizeMsg(s) {
    if (s === undefined || s === null) return ""
    const literal = String.fromCharCode(96) + "n"
    return String(s).split(literal).join("\n")
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 4
    spacing: 6

    LogHead {
      autoScroll: root.autoScroll
      onAutoScrollChanged: root.autoScroll = autoScroll
    }

    Item {
      Layout.fillWidth: true
      Layout.fillHeight: true
      Frame{
        anchors.fill: parent
      }
      ListView {
        id: list
        anchors.fill: parent
        anchors.margins: 1
        clip: true
        spacing: 2
        model: Datas.LogDatas.filteredLogs

        delegate: Item {
          width: list.width
          property string rawLevel: level !== undefined ? level : (Level !== undefined ? Level : "")
          property string levelText: String(rawLevel).toUpperCase()
          property string loggerName: String(name !== undefined ? name : (logger !== undefined ? logger : ""))
          property real timestampValue: Number(ts !== undefined ? ts : (timestamp !== undefined ? timestamp : 0))
          property string stampText: (time !== undefined && String(time).length > 0)
                                      ? String(time)
                                      : (timestampValue > 0 ? new Date(timestampValue * 1000).toLocaleString() : "")
          property var stampParts: stampText.length > 0 ? stampText.split(/\s+/) : []
          property string stampDisplay: stampParts.length > 0 ? stampParts[stampParts.length - 1] : "-"
          property color textColor: {
            switch (levelText) {
            case "ERROR":
              return Cores.CoreStyle.danger
            case "WARN":
            case "WARNING":
              return Cores.CoreStyle.warning
            case "DEBUG":
              return Cores.CoreStyle.accent
            default:
              return Cores.CoreStyle.success
            }
          }
          readonly property color backgroundColor: Qt.rgba(textColor.r, textColor.g, textColor.b, 0.12)
          readonly property string messageText: normalizeMsg(
                                                  msg !== undefined ? msg :
                                                  (message !== undefined ? message : ""))


          implicitHeight: contentRow.implicitHeight + 2

          RowLayout {
            id: contentRow
            anchors.fill: parent
            anchors.margins: 8
            spacing: 10

            Label {
              text: stampDisplay
              color: Cores.CoreStyle.muted
              Layout.preferredWidth: 92
            }

            Label {
              text: levelText.length > 0 ? levelText : "-"
              color: textColor
              font.bold: levelText === "ERROR" || levelText === "WARN" || levelText === "WARNING"
              Layout.preferredWidth: 70
            }

            Label {
              text: loggerName.length > 0 ? loggerName : "-"
              color: Qt.tint(Cores.CoreStyle.muted, Qt.rgba(textColor.r, textColor.g, textColor.b, 0.25))
              Layout.preferredWidth: 150
              elide: Label.ElideRight
            }

            Label {
              text: messageText.length > 0 ? messageText : "-"
              color: Cores.CoreStyle.text
              Layout.fillWidth: true
              wrapMode: Text.WordWrap
            }
          }
        }

        ScrollBar.vertical: ScrollBar { }
      }
    }
  }

  Connections {
    target: Datas.LogDatas
    function onLogReceived(item) {
      if (root.autoScroll && Datas.LogDatas.matchesFilter(item))
        list.positionViewAtEnd()
    }

    function onFilteredAboutToUpdate() {
      if (!root.autoScroll) {
        var bottomOffset = list.contentHeight - list.contentY - list.height
        root.preservedBottomOffset = Math.max(0, bottomOffset)
      }
    }
    function onFilteredUpdated() {
      if (root.autoScroll) {
        list.positionViewAtEnd()
      } else {
        Qt.callLater(function() {
          var contentHeight = list.contentHeight
          var viewHeight = list.height
          var maxY = Math.max(0, contentHeight - viewHeight)
          var targetY = Math.max(0, maxY - root.preservedBottomOffset)
          list.contentY = targetY
        })
      }
    }
  }
}






