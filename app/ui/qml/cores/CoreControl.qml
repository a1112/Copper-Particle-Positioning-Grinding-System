pragma Singleton
import QtQuick
import QtQml
import "../Api" as Api
import "." as CoreSingletons

Item {
  id: coreControl

  property var cylinderStates: []
  property bool allowDirectControl: false
  property bool allowJogging: false

  function _ensureCylinderStates() {
    if (!Array.isArray(cylinderStates) || cylinderStates.length !== 16) {
      var arr = []
      for (var i = 0; i < 16; ++i)
        arr.push(false)
      cylinderStates = arr
    }
  }

  function _directControlEnabled() {
    if (allowDirectControl)
      return true
    console.warn("Direct device control is disabled via settings.")
    return false
  }

  function _jogEnabled() {
    if (allowJogging)
      return true
    console.warn("Jog commands are disabled via settings.")
    return false
  }

  function setSpeed(vFast, vWork){
    if (!_directControlEnabled())
      return
    try { Api.ApiClient.setSpeed(vFast, vWork, function(){}, function(){}) } catch(e){}
  }

  function jog(axis, direction, speed){
    if (!_jogEnabled())
      return
    try { Api.ApiClient.jog(axis, direction, speed, function(){}, function(){}) } catch(e){}
  }

  function home(){
    if (!_directControlEnabled())
      return
    try { Api.ApiClient.home(function(){}, function(){}) } catch(e){}
  }

  function setWorkOrigin(){
    if (!_directControlEnabled())
      return
    try { Api.ApiClient.setWorkOrigin(function(){}, function(){}) } catch(e){}
  }

  function reset(){
    try { Api.ApiClient.control('reset', {}, function(){}, function(){}) } catch(e){}
  }

  function estop(){
    try { Api.ApiClient.control('estop', {}, function(){}, function(){}) } catch(e){}
  }

  function isCylinderOpen(index) {
    _ensureCylinderStates()
    var idx = Number(index)
    if (isNaN(idx) || idx < 0 || idx >= cylinderStates.length)
      return false
    return !!cylinderStates[idx]
  }

  function _applyCylinderState(index, open) {
    _ensureCylinderStates()
    var idx = Number(index)
    if (isNaN(idx) || idx < 0 || idx >= cylinderStates.length)
      return
    var next = cylinderStates.slice()
    next[idx] = !!open
    cylinderStates = next
  }

  function _applyAllCylinders(open) {
    var arr = []
    for (var i = 0; i < 16; ++i)
      arr.push(!!open)
    cylinderStates = arr
  }

  function setCylinder(index, open) {
    if (!_directControlEnabled())
      return
    var idx = Number(index)
    if (isNaN(idx) || idx < 0 || idx >= 16)
      return
    var target = !!open
    try {
      Api.ApiClient.setCylinder(idx, target, function() { _applyCylinderState(idx, target) }, function(status, message) {
        console.warn("cylinder.set failed", status, message)
      })
    } catch (err) {
      console.warn("cylinder.set threw", err)
    }
  }

  function toggleCylinder(index) {
    if (!_directControlEnabled())
      return
    var target = !isCylinderOpen(index)
    setCylinder(index, target)
  }

  function setAllCylinders(open) {
    if (!_directControlEnabled())
      return
    var target = !!open
    try {
      Api.ApiClient.setAllCylinders(target, function() { _applyAllCylinders(target) }, function(status, message) {
        console.warn("cylinder.set_all failed", status, message)
      })
    } catch (err) {
      console.warn("cylinder.set_all threw", err)
    }
  }

  function openAllCylinders() {
    setAllCylinders(true)
  }

  function closeAllCylinders() {
    setAllCylinders(false)
  }

  function updateCylinderStates(states) {
    if (!Array.isArray(states))
      return
    var arr = []
    for (var i = 0; i < 16; ++i) {
      var value = states[i]
      arr.push(value === true || value === 1 || value === "1" || value === "true")
    }
    cylinderStates = arr
  }

  function _deviceAreaConfig() {
    var general = CoreSingletons.CoreSettings ? CoreSingletons.CoreSettings.parameterGeneral : {}
    if (!general || typeof general !== "object")
      return {}
    if (general.device_area && typeof general.device_area === "object")
      return general.device_area
    if (general.deviceArea && typeof general.deviceArea === "object")
      return general.deviceArea
    return {}
  }

  function refreshPermissions() {
    var area = _deviceAreaConfig()
    if (area.hasOwnProperty("allow_direct_control"))
      allowDirectControl = !!area.allow_direct_control
    else if (area.hasOwnProperty("allowDirectControl"))
      allowDirectControl = !!area.allowDirectControl
    else
      allowDirectControl = false

    if (area.hasOwnProperty("allow_jog"))
      allowJogging = allowDirectControl && !!area.allow_jog
    else if (area.hasOwnProperty("allowJog"))
      allowJogging = allowDirectControl && !!area.allowJog
    else
      allowJogging = false
  }

  Component.onCompleted: refreshPermissions()

  Connections {
    target: CoreSingletons.CoreSettings
    function onParameterGeneralChanged() { coreControl.refreshPermissions() }
  }
}
