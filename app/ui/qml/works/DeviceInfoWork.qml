pragma Singleton
import QtQuick
import "../Api" as Api
import "../datas" as Datas

QtObject {
  id: root

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
    _fetchToolInfo()
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

  function _fetchToolInfo() {
    Api.ApiClient.toolInfo(function(payload) {
      try {
        if (!payload)
          return
        Datas.ToolInfoData.applySnapshot(payload)
      } catch (err) {
        console.warn("DeviceInfoWork toolInfo apply failed", err)
      }
    }, function(status, message) {
      console.warn("DeviceInfoWork toolInfo error", status, message)
    })
  }
}
