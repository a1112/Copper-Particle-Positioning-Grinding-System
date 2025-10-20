import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../datas" as Datas
import "../Base"
import "../../cores" as Cores

BaseCard {
  id: root

  property bool autoScroll: true
  property int maxRows: 1000

  // Normalize server log messages that may contain literal backtick-n sequences
  function normalizeMsg(s) {
    if (s === undefined || s === null) return ""
    const literal = String.fromCharCode(96) + "n"
    return String(s).split(literal).join("\n")
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 8
    spacing: 6

    LogHead { autoScroll: root.autoScroll; onAutoScrollChanged: root.autoScroll = autoScroll }

    Frame {
      Layout.fillWidth: true
      Layout.fillHeight: true
      padding: 6

      ListView {
        id: list
        anchors.fill: parent
        anchors.margins: 2
        clip: true
        spacing: 4
        model: Datas.LogDatas.filteredLogs

        delegate: Rectangle {
          width: list.width
          radius: 6
          color: backgroundColor
          border.width: 1
          border.color: Qt.alpha(textColor, 0.35)
          property var entry: modelData || ({})
          property string levelText: String(entry.level !== undefined ? entry.level : (entry.Level || "")).toUpperCase()
          property string loggerName: String(entry.name !== undefined ? entry.name : (entry.logger || ""))
          property real timestamp: Number(entry.ts !== undefined ? entry.ts : entry.timestamp || 0)
          property string stampText: (entry.time && String(entry.time).length > 0)
                                      ? String(entry.time)
                                      : (timestamp > 0 ? new Date(timestamp * 1000).toLocaleString() : "")
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

          implicitHeight: contentRow.implicitHeight + 16

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
              text: normalizeMsg(entry.msg !== undefined ? entry.msg : (entry.message || ""))
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
    function onFilteredLogsChanged() {
      if (root.autoScroll)
        list.positionViewAtEnd()
    }
  }
}





