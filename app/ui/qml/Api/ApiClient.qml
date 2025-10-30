pragma Singleton
import QtQuick
                                                                                                import "../js/Http.js" as Http

QtObject {
  id: apiClient
  // Root window for timers and dialogs
  property var root
  // Error popup hook provided by root
  property var showError

  function setBase(url){ Http.base = url }
  function setTimeout(ms){ Http.timeoutMs = ms }

  // GET
  function get(path, onOk, onErr){ Http.get(root, path, onOk, onErr, showError) }
  // POST JSON
  function post(path, body, onOk, onErr){ Http.postJson(root, path, body, onOk, onErr, showError) }
  // DELETE
  function del(path, onOk, onErr){ Http.del(root, path, onOk, onErr, showError) }

  function control(action,params,onOk, onErr){
    post('/control', {"action":action,"params":params}, onOk, onErr)
  }

  // Convenience APIs
  function startRun(onOk, onErr){ control('start', {}, onOk, onErr) }
  function stopRun(onOk, onErr){ control('stop', {}, onOk, onErr) }
  function setSpeed(vFast, vWork, onOk, onErr){ control('motion.set_speed', { v_fast: vFast, v_work: vWork }, onOk, onErr) }
  function jog(axis, dir, speed, onOk, onErr){ control('motion.jog', { axis: axis, direction: dir, speed: speed }, onOk, onErr) }
  function home(onOk, onErr){ control('motion.home', {}, onOk, onErr) }
  function setWorkOrigin(onOk, onErr){ control('motion.set_work_origin', {}, onOk, onErr) }
  function status(onOk, onErr){ get('/status', onOk, onErr) }
  function configSettings(onOk, onErr){ get('/config/settings', onOk, onErr) }
  function toolList(onOk, onErr){ get('/toolList', onOk, onErr) }
  function calibration(onOk, onErr){ get('/vision/calibration', onOk, onErr) }
  // Test images
  function listTestImages(onOk, onErr){ get('/test/images', onOk, onErr) }
  function loadTestImage(name, onOk, onErr){ post('/test/load_image?name=' + encodeURIComponent(name), {}, onOk, onErr) }
  function loadDefaultImage(onOk, onErr){ post('/test/load_default', {}, onOk, onErr) }

  // Test groups
  function listGroups(onOk, onErr){ get('/test/group/list', onOk, onErr) }
  function listGroupImages(serial, onOk, onErr){ get('/test/group/' + encodeURIComponent(serial) + '/images', onOk, onErr) }
  function createGroup(serial, note, onOk, onErr){ post('/test/group/create', { serial: serial, note: note }, onOk, onErr) }
  function addImageToGroup(serial, name, onOk, onErr){ post('/test/group/' + encodeURIComponent(serial) + '/add_image?name=' + encodeURIComponent(name), {}, onOk, onErr) }
}

