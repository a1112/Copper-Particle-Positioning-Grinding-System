pragma Singleton
import QtQuick

QtObject {
  id: root
  property int status: -1
  property bool connected: false
  property int lastMsgTs: 0
  property var lastMessage: ({})
  property var seriesA: []
  property var seriesB: []
  property int seriesLimit: 1000
  signal messageReceived(var payload)

  function reset() {
    lastMsgTs = 0
    lastMessage = ({})
    seriesA = []
    seriesB = []
  }

  function pushSeries(target, value) {
    if (!target || value === undefined || value === null || isNaN(value))
      return
    target.push(Number(value))
    if (target.length > seriesLimit)
      target.shift()
  }

  function ingest(payload) {
    lastMsgTs = Date.now()
    lastMessage = payload || ({})
    if (payload && payload.seriesA !== undefined)
      pushSeries(seriesA, payload.seriesA)
    if (payload && payload.seriesB !== undefined)
      pushSeries(seriesB, payload.seriesB)
    messageReceived(payload)
  }
}
