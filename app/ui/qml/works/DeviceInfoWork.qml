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
        Datas.DeviceInfoData.applySnapshot({
          runState: payload.state,
          runMode: payload.mode || payload.run_mode,
          serialNumber: payload.serial_number || payload.serialNumber,
          toolUsage: payload.tool_usage || payload.toolUsage
        })
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
        Datas.DeviceInfoData.applySnapshot({
          serialNumber: payload.board_serial || payload.boardSerial,
          toolDiameter: payload.cutter_diameter || payload.cutterDiameter,
          toolLifetime: payload.tool_life || payload.toolLife,
          particleTotal: payload.particle_count || payload.particleTotal,
          planeHeight: payload.plane_height || payload.planeHeight
        })
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
        if (!payload || !payload.tool_table || !payload.tool_table.length)
          return
        var first = payload.tool_table[0]
        Datas.DeviceInfoData.applySnapshot({
          toolModel: first.name || first.code || "-"
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
