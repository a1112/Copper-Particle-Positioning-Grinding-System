pragma Singleton
import QtQuick
import "../Api" as Api
import "../datas" as Datas
import "../cores" as Cores

QtObject {
  id: root

  property Timer pollTimer: Timer {
    id: poll
    interval: 1000
    running: false
    repeat: true
    onTriggered: root.fetch()
  }

  function fetch() {
    Api.ApiClient.get('/cutting', function(resp) {
      if (resp) {
        Cores.CoreCutting.updateCuttingSnapshot(resp)
        Datas.CuttingDatas.update(resp)
      } else {
        Cores.CoreCutting.resetCuttingSnapshot()
      }
    }, function() {
      Cores.CoreCutting.resetCuttingSnapshot()
      Datas.CuttingDatas.reset()
    })
  }

  function start() {
    if (!pollTimer.running) {
      pollTimer.start()
      fetch()
    }
  }

  function stop() {
    pollTimer.stop()
    Cores.CoreCutting.resetCuttingSnapshot()
    Datas.CuttingDatas.reset()
  }

  function reconnect() {
    stop()
    start()
  }
}
