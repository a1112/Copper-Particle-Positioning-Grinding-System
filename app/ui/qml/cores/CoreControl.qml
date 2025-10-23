pragma Singleton
import QtQuick
import "../Api" as Api


QtObject {
  id: coreControl


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
    try { Api.ApiClient.post('/control/reset', {}, function(){}, function(){}) } catch(e){}
  }

  function estop(){
    try { Api.ApiClient.post('/control/estop', {}, function(){}, function(){}) } catch(e){}
  }
}
