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
  property real maxSpindleRpm: 0
  signal messageReceived(var payload)

  function reset() {
    status = -1
    connected = false
    lastMsgTs = 0
    lastMessage = ({})
    seriesA = []
    seriesB = []
    maxSpindleRpm = 0
  }

  function pushSeries(target, value) {
    if (!target)
      return
    var num = Number(value)
    if (isNaN(num))
      return
    target.push(num)
    if (target.length > seriesLimit)
      target.shift()
  }

  function ingest(payload) {
    connected = true
    lastMsgTs = Date.now()
    lastMessage = payload || ({})

    var rpmCandidate
    if (payload) {
      if (payload.seriesA !== undefined)
        rpmCandidate = payload.seriesA
      else if (payload.spindle_rpm !== undefined)
        rpmCandidate = payload.spindle_rpm
    }
    if (rpmCandidate !== undefined)
      pushSeries(seriesA, rpmCandidate)

    var torqueCandidate
    if (payload) {
      if (payload.seriesB !== undefined)
        torqueCandidate = payload.seriesB
      else if (payload.spindle_torque !== undefined)
        torqueCandidate = payload.spindle_torque
    }
    if (torqueCandidate !== undefined)
      pushSeries(seriesB, torqueCandidate)

    if (rpmCandidate !== undefined) {
      var rpmValue = Number(rpmCandidate)
      if (!isNaN(rpmValue) && rpmValue > maxSpindleRpm)
        maxSpindleRpm = rpmValue
    }

    messageReceived(payload)
  }
}
