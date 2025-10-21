import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../cores" as Cores
import "../../datas" as Datas
import "../../works" as Works
import "../../components/btns" as Btns
import "../../components/Base" as BaseComponents

Item {
  id: root
  height: Cores.CoreStyle.cardHeadHeight
  Layout.fillWidth: true

  property bool autoScroll: true

  ListModel {
    id: levelOptions
    ListElement { text: qsTr("全部"); value: "ALL" }
    ListElement { text: qsTr("INFO 及以上"); value: "INFO" }
    ListElement { text: qsTr("WARN 及以上"); value: "WARN" }
    ListElement { text: qsTr("ERROR"); value: "ERROR" }
  }

  RowLayout {
    anchors.fill: parent
    spacing: 10

    Label {
      text: qsTr("日志")
      font.bold: true
      color: Cores.CoreStyle.text
    }

    Rectangle {
      width: 10
      height: 10
      radius: 5
      color: Datas.LogDatas.connected ? Cores.CoreStyle.success : Cores.CoreStyle.danger
    }

    Label {
      text: Datas.LogDatas.connected ? qsTr("已连接") : qsTr("未连接")
      color: Datas.LogDatas.connected ? Cores.CoreStyle.success : Cores.CoreStyle.danger
    }

    Label {
      text: qsTr("显示等级")
      color: Cores.CoreStyle.muted
    }

    BaseComponents.ComboBoxBase {
      id: levelCombo
      model: levelOptions
      textRole: "text"
      valueRole: "value"
      Layout.preferredWidth: 150

      function syncFromFilter() {
        var value = String(Datas.LogDatas.levelFilter || "ALL").toUpperCase()
        var idx = 0
        for (var i = 0; i < levelOptions.count; ++i) {
          if (String(levelOptions.get(i).value || "").toUpperCase() === value) {
            idx = i
            break
          }
        }
        if (currentIndex !== idx)
          currentIndex = idx
      }

      onActivated: {
        var element = levelOptions.get(currentIndex)
        Datas.LogDatas.levelFilter = element ? element.value : "ALL"
      }

      Component.onCompleted: syncFromFilter()
    }

    Connections {
      target: Datas.LogDatas
      function onLevelFilterChanged() {
        levelCombo.syncFromFilter()
      }
    }

    Item { Layout.fillWidth: true }

    BaseComponents.CheckDelegateBase {
      text: qsTr("自动滚动")
      checked: root.autoScroll
      onCheckedChanged: root.autoScroll = checked
    }

    Btns.ActionButton {
      text: qsTr("清空本地")
      onClicked: Works.LogsWork.clearLocalLogs()
    }

    Btns.ActionButton {
      text: qsTr("清空服务器")
      onClicked: Works.LogsWork.clearServerLogs()
    }
  }
}
