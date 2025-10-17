import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../Base"
import "../../cores" as Cores
import "../Charts" as Charts
import "../../Api" as Api

BaseCard {
    id: root
    // demo data for elevation until backend is wired
    property var demoPts: (function(){ var arr=[]; var L=100; for (var i=0;i<=L;i++){ var s=i; var z = -Math.abs(Math.sin(i/10))*0.8; arr.push({s:s,z:z}); } return arr })()
    property var demoCuts: ([{s:10,z:-0.2},{s:30,z:-0.5},{s:60,z:-0.3},{s:85,z:-0.7}])
    property var machineMeta: ({})
    property var elevPts: []
    property var elevCuts: []
    property real elevBase: 0.0
    Component.onCompleted:
    {
        Api.ApiClient.get('/config/meta',
                          function(r){
                            root.machineMeta = r||{} }
                          , function(s,m){
                            console.log('meta err', s, m) });

        Api.ApiClient.get('/path/elevation',
                          function(r){
                            root.elevPts = (r && r.points)||[];
                            root.elevCuts = (r && r.cuts)||[];
                            root.elevBase = (r && typeof r.base === 'number') ? r.base : 0.0 },
                          function(s,m){
                            console.log('elev err', s, m) })
    }
        GridLayout { id: gridInfo; columns: 3; rowSpacing: 4; columnSpacing: 24
          // 每格一个“名: 值”对
          RowLayout { Label { text: "流水号"; color: "#b8c"; Layout.preferredWidth: 72 }
            Label { text: (root.machineMeta.board_serial || '-') }
          }

          RowLayout { Label { text: "平面高度"; color: "#b8c"; Layout.preferredWidth: 72 }
            Label { text: (root.machineMeta.plane_height || '-') }
          }

          RowLayout { Label { text: "粒子数量"; color: "#b8c"; Layout.preferredWidth: 72 }
            Label { text: (root.machineMeta.particle_count || '-') }
          }

          RowLayout { Label { text: "刀盘"; color: "#b8c"; Layout.preferredWidth: 72 }
            Label { text: (root.machineMeta.cutter_diameter || '-') }
          }
          RowLayout { Label { text: "寿命"; color: "#b8c"; Layout.preferredWidth: 72 }
            Label { text: (root.machineMeta.tool_life || '-') }
          }
          RowLayout { Label { text: "控制"; color: "#b8c"; Layout.preferredWidth: 72 }
            Label { text: (root.machineMeta.control_mode || '-') }
          }

          }
      }

