import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtWebSockets
import QtCore
import "../Base"
import "../../Api" as Api
import "../../cores" as Cores
import "../../components/btns" as Btns

BaseCard {
  id: root

  // Program model: each row is one instruction line and its status
  ListModel { id: codeModel }
  property int currentIndex: -1
  property string runState: 'IDLE'   // IDLE/RUNNING/PAUSED
  // WS connection state for code channel
  property bool codeConnected: (wsCode.status===WebSocket.Open)

  function setProgram(lines){
    codeModel.clear()
    for (var i=0;i<lines.length;i++){
      codeModel.append({ idx: i+1, text: String(lines[i]), status: 'READY', msg: '' })
    }
  }

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 8
    spacing: 8


    CodeHead{

    }

    RowLayout {
      Layout.fillWidth: true
      spacing: 12
      Label { text: '指令'; color: Cores.CoreStyle.text; font.bold: true; Layout.fillWidth: true }
      // Connection status for /ws/code
      Rectangle { width: 10; height: 10; radius: 5; color: root.codeConnected ? Cores.CoreStyle.success : Cores.CoreStyle.danger }
      Label { text: (root.codeConnected ? '已连接' : '未连接'); color: (root.codeConnected ? Cores.CoreStyle.success : Cores.CoreStyle.danger) }
      Label { text: '状态: ' + runState; color: (runState==='RUNNING'? Cores.CoreStyle.success : Cores.CoreStyle.muted) }
      Label { text: (currentIndex>=0 ? ('当前: ' + (currentIndex+1)) : '当前: -'); color: Cores.CoreStyle.muted }
      Btns.ActionButton { text: '运行'; onClicked: Api.ApiClient.startRun() }
      Btns.ActionButton { text: '停止'; danger: true; onClicked: Api.ApiClient.stopRun() }
    }

    // Program list with inline editing
    Frame {
      clip: true
      Layout.fillWidth: true
      Layout.fillHeight: true
      padding: 6
      ListView {
        id: list
        anchors.fill: parent
        model: codeModel
        delegate: RowLayout {
          width: list.width
          spacing: 8
          Rectangle { width: 36; height: 28; radius: 4; color: (index===root.currentIndex ? Cores.CoreStyle.accent : Cores.CoreStyle.surface)
            Label { anchors.centerIn: parent; text: idx; color: (index===root.currentIndex ? 'black' : Cores.CoreStyle.text) }
          }
          TextField {
            id: lineEdit
            Layout.fillWidth: true
            text: model.text
            color: Cores.CoreStyle.text
            onEditingFinished: { model.text = text }
          }
          Label {
            text: model.status
            color: (model.status==='RUNNING' ? Cores.CoreStyle.accent : (model.status==='OK' ? Cores.CoreStyle.success : (model.status==='FAIL' ? Cores.CoreStyle.danger : Cores.CoreStyle.muted)))
            Layout.preferredWidth: 68
          }
        }
        ScrollBar.vertical: ScrollBar {}
      }
    }
  }

  // WebSocket to receive execution info
  WebSocket {
    id: wsCode
    url: Api.Urls.wsCode()
    active: true
    onStatusChanged: function(status){ /* trigger binding update */ root.codeConnected = (status===WebSocket.Open) }
    onTextMessageReceived: function(message){
      try {
        var p = JSON.parse(message)
        if (p.type === 'program' && Array.isArray(p.lines)) {
          setProgram(p.lines)
        } else if (p.type === 'state') {
          root.runState = p.state || 'IDLE'
          root.currentIndex = (p.current!==undefined ? p.current : -1)
          // update statuses
          for (var i=0;i<codeModel.count;i++){
            var st = (i===root.currentIndex ? 'RUNNING' : (i<root.currentIndex ? 'OK' : 'READY'))
            codeModel.setProperty(i, 'status', st)
          }
        } else if (p.type === 'result') {
          if (p.index!==undefined) {
            codeModel.setProperty(p.index, 'status', (p.ok? 'OK':'FAIL'))
            if (p.msg) codeModel.setProperty(p.index, 'msg', p.msg)
          }
        }
      } catch(e) { /* ignore */ }
    }
  }
}
