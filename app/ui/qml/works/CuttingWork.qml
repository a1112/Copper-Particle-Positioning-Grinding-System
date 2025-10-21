pragma Singleton
import QtQuick
import "../Api" as Api
import "../datas" as Datas

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
        Datas.CuttingDatas.update(resp)
      }
    }, function() {
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
    Datas.CuttingDatas.reset()
  }

  function reconnect() {
    stop()
    start()
  }
}
