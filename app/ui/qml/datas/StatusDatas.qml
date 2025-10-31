pragma Singleton
import QtQuick
// Data contract details: see docs/ui_data_contracts.md (status payload section)

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
  property bool forceEnableControls: false
  property bool internalControlEnabled: true
  property bool controlEnabled: forceEnableControls || internalControlEnabled
  signal messageReceived(var payload)

  function reset() {
    status = -1
    connected = false
    lastMsgTs = 0
    lastMessage = ({})
    seriesA = []
    seriesB = []
    maxSpindleRpm = 0
    internalControlEnabled = true
    forceEnableControls = false
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
    lastMessage = payload
    internalControlEnabled = resolveControlEnabled(payload)

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

  function resolveControlEnabled(payload) {
    if (!payload)
      return internalControlEnabled

    var modeCode = payload.control_mode_code !== undefined ? Number(payload.control_mode_code) : null
    if (modeCode !== null && !isNaN(modeCode))
      return modeCode === 1

    var candidates = []
    if (payload.control_mode !== undefined)
      candidates.push(String(payload.control_mode))
    if (payload.run_mode !== undefined)
      candidates.push(String(payload.run_mode))
    if (payload.runMode !== undefined)
      candidates.push(String(payload.runMode))

    for (var i = 0; i < candidates.length; ++i) {
      var text = (candidates[i] || "").toString().trim().toUpperCase()
      if (!text)
        continue
      if (text.indexOf("REMOTE") !== -1 || text === "HTTP")
        return true
      if (text === "LOCAL" || text === "LOCKED")
        return false
    }
    return internalControlEnabled;
  }
}
