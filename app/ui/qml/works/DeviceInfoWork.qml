pragma Singleton
import QtQuick
import "../Api" as Api
import "../datas" as Datas

QtObject {
  id: root

  property bool _settingsLoaded: false

  property Timer _refreshTimer: Timer {
    id: refreshTimer
    interval: 5000
    running: false
    repeat: true
    onTriggered: root.refresh()
  }

  function _isEmpty(value) {
    if (value === undefined)
      return true
    if (value === null)
      return true
    return value === ""
  }

  function start() {
    refresh()
    if (!refreshTimer.running)
      refreshTimer.start()
  }

  function stop() {
    refreshTimer.stop()
  }

  function refresh() {
    _fetchStatus()
    _fetchMeta()
    if (!_settingsLoaded)
      _fetchSettings()
  }

  function _fetchStatus() {
    Api.ApiClient.status(function(payload) {
      try {
        if (!payload)
          return
        var snapshot = {
          runState: payload.state
        }
        if (payload.mode !== undefined)
          snapshot.runMode = payload.mode
        else if (payload.run_mode !== undefined)
          snapshot.runMode = payload.run_mode
        if (payload.serial_number !== undefined)
          snapshot.serialNumber = payload.serial_number
        else if (payload.serialNumber !== undefined)
          snapshot.serialNumber = payload.serialNumber
        if (payload.tool_usage !== undefined)
          snapshot.toolUsage = payload.tool_usage
        else if (payload.toolUsage !== undefined)
          snapshot.toolUsage = payload.toolUsage
        Datas.DeviceInfoData.applySnapshot(snapshot)
      } catch (err) {
        console.warn("DeviceInfoWork status apply failed", err)
      }
    }, function(status, message) {
      console.warn("DeviceInfoWork status error", status, message)
    })
  }

  function _fetchMeta() {
    Api.ApiClient.get("/config/meta", function(payload) {
      try {
        if (!payload)
          return
        var metaSnapshot = {}
        if (payload.board_serial !== undefined)
          metaSnapshot.serialNumber = payload.board_serial
        else if (payload.boardSerial !== undefined)
          metaSnapshot.serialNumber = payload.boardSerial
        if (payload.cutter_diameter !== undefined)
          metaSnapshot.toolDiameter = payload.cutter_diameter
        else if (payload.cutterDiameter !== undefined)
          metaSnapshot.toolDiameter = payload.cutterDiameter
        if (payload.tool_life !== undefined)
          metaSnapshot.toolLifetime = payload.tool_life
        else if (payload.toolLife !== undefined)
          metaSnapshot.toolLifetime = payload.toolLife
        if (payload.particle_count !== undefined)
          metaSnapshot.particleTotal = payload.particle_count
        else if (payload.particleTotal !== undefined)
          metaSnapshot.particleTotal = payload.particleTotal
        if (payload.plane_height !== undefined)
          metaSnapshot.planeHeight = payload.plane_height
        else if (payload.planeHeight !== undefined)
          metaSnapshot.planeHeight = payload.planeHeight
        Datas.DeviceInfoData.applySnapshot(metaSnapshot)
      } catch (err) {
        console.warn("DeviceInfoWork meta apply failed", err)
      }
    }, function(status, message) {
      console.warn("DeviceInfoWork meta error", status, message)
    })
  }

  function _fetchSettings() {
    Api.ApiClient.configSettings(function(payload) {
      try {
        if (!payload)
          return
        if (!payload.tool_table)
          return
        if (!payload.tool_table.length)
          return
        var first = payload.tool_table[0]
        var toolModelValue = first.name
        if (_isEmpty(toolModelValue))
          toolModelValue = first.code
        if (_isEmpty(toolModelValue))
          toolModelValue = "-"
        Datas.DeviceInfoData.applySnapshot({
          toolModel: toolModelValue
        })
        _settingsLoaded = true
      } catch (err) {
        console.warn("DeviceInfoWork settings apply failed", err)
      }
    }, function(status, message) {
      console.warn("DeviceInfoWork settings error", status, message)
    })
  }
}
