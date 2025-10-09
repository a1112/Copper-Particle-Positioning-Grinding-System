import QtQuick 2.15
import "./Http.js" as Http

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

  // Convenience APIs
  function startRun(onOk, onErr){ post('/run/start', {}, onOk, onErr) }
  function stopRun(onOk, onErr){ post('/run/stop', {}, onOk, onErr) }
  function setSpeed(vFast, vWork, onOk, onErr){ post('/motion/set_speed', { v_fast: vFast, v_work: vWork }, onOk, onErr) }
  function jog(axis, dir, speed, onOk, onErr){ post('/motion/jog', { axis: axis, direction: dir, speed: speed }, onOk, onErr) }
  function home(onOk, onErr){ post('/motion/home', {}, onOk, onErr) }
  function setWorkOrigin(onOk, onErr){ post('/motion/set_work_origin', {}, onOk, onErr) }
  function status(onOk, onErr){ get('/status', onOk, onErr) }
}
