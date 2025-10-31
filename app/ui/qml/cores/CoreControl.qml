pragma Singleton
import QtQuick
import "../Api" as Api


QtObject {
  id: coreControl

  property var cylinderStates: []

  function _ensureCylinderStates() {
    if (!Array.isArray(cylinderStates) || cylinderStates.length !== 16) {
      var arr = []
      for (var i = 0; i < 16; ++i)
        arr.push(false)
      cylinderStates = arr
    }
  }

  function setSpeed(vFast, vWork){
    try { Api.ApiClient.setSpeed(vFast, vWork, function(){}, function(){}) } catch(e){}
  }

  function jog(axis, direction, speed){
    try { Api.ApiClient.jog(axis, direction, speed, function(){}, function(){}) } catch(e){}

  }

  function home(){
    try { Api.ApiClient.home(function(){}, function(){}) } catch(e){}

  }

  function setWorkOrigin(){
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
    var target = !isCylinderOpen(index)
    setCylinder(index, target)
  }

  function setAllCylinders(open) {
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
}
