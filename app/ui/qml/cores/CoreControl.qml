pragma Singleton
import QtQuick
import "../Api" as Api

// Core control bridge for motion and safety actions.
// Prefer HTTP API via Api.ApiClient; fall back to `backend` slots when available.
QtObject {
  id: coreControl

  function _hasBackend(){ try { return typeof backend !== 'undefined' && backend !== null } catch(e){ return false } }

  function setSpeed(vFast, vWork){
    try { Api.ApiClient.setSpeed(vFast, vWork, function(){}, function(){}) } catch(e){}
    if (_hasBackend()) try { backend.setSpeed(vFast, vWork) } catch(e){}
  }

  function jog(axis, direction, speed){
    try { Api.ApiClient.jog(axis, direction, speed||10, function(){}, function(){}) } catch(e){}
    if (_hasBackend()) try { backend.jog(axis, direction) } catch(e){}
  }

  function home(){
    try { Api.ApiClient.home(function(){}, function(){}) } catch(e){}
    if (_hasBackend()) try { backend.home() } catch(e){}
  }

  function setWorkOrigin(){
    try { Api.ApiClient.setWorkOrigin(function(){}, function(){}) } catch(e){}
    if (_hasBackend()) try { backend.setWorkOrigin() } catch(e){}
  }

  function reset(){
    try { Api.ApiClient.post('/control/reset', {}, function(){}, function(){}) } catch(e){}
  }

  function estop(){
    try { Api.ApiClient.post('/control/estop', {}, function(){}, function(){}) } catch(e){}
  }
}

