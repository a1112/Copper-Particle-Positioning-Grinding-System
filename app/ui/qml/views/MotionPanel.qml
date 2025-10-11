import QtQuick\nimport QtQuick.Controls\nimport "../Api" as Api\n\nimport QtQuick.Controls
import QtQuick.Layouts

Item {
  id: root
  // api client injected by parent loader (ApiClient.qml instance)
    Column {
    spacing: 6
    Row { spacing: 6
      Label { text: "快移(mm/s)" }
      SpinBox { id: vFast; from: 1; to: 500; value: 100; stepSize: 1 }
      Label { text: "工进(mm/s)" }
      SpinBox { id: vWork; from: 0; to: 100; value: 10; stepSize: 1 }
      Button { text: "设置速度"; onClicked: Api.ApiClient.setSpeed(vFast.value, vWork.value, function(_){}, function(s,m){ console.log('set_speed err', s, m) }) }
    }
    GridLayout { columns: 4
      Button { text: "X-"; onClicked: Api.ApiClient.jog('x', -1, vFast.value, function(_){}, function(s,m){ console.log('jog err', s, m) }) }
      Button { text: "Y+"; onClicked: Api.ApiClient.jog('y', 1, vFast.value, function(_){}, function(s,m){ console.log('jog err', s, m) }) }
      Button { text: "X+"; onClicked: Api.ApiClient.jog('x', 1, vFast.value, function(_){}, function(s,m){ console.log('jog err', s, m) }) }
      Button { text: "Y-"; onClicked: Api.ApiClient.jog('y', -1, vFast.value, function(_){}, function(s,m){ console.log('jog err', s, m) }) }
    }
    Row { spacing: 6
      Button { text: "回零"; onClicked: Api.ApiClient.home(function(_){}, function(s,m){ console.log('home err', s, m) }) }
      Button { text: "设工件原点"; onClicked: Api.ApiClient.setWorkOrigin(function(_){}, function(s,m){ console.log('set_work_origin err', s, m) }) }
      Label { text: backend.posText }
    }
  }
}


