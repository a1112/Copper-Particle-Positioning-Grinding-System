// Lightweight HTTP helpers with timeout and error popup callback
.pragma library

var base = "http://127.0.0.1:8000"
var timeoutMs = 5000

function _makeTimer(root, ms, onTimeout){
  var t = Qt.createQmlObject('import QtQuick 2.15; Timer { interval: '+ms+'; repeat: false }', root)
  t.triggered.connect(function(){ try{ onTimeout&&onTimeout() } finally { t.destroy() } })
  t.start()
  return t
}

function get(root, path, onOk, onErr, showError){
  var xhr = new XMLHttpRequest()
  var timedOut = false
  var to = _makeTimer(root, timeoutMs, function(){
    timedOut = true
    try{ xhr.abort() }catch(e){}
    var msg = 'GET ' + path + ' 超时(' + timeoutMs + 'ms)'
    showError && showError(msg)
    onErr && onErr(408, msg)
  })
  xhr.open('GET', base + path)
  xhr.onreadystatechange = function(){
    if (xhr.readyState === XMLHttpRequest.DONE){
      try{ to.stop(); to.destroy() }catch(e){}
      if (timedOut) return
      if (xhr.status>=200 && xhr.status<300){
        try{ onOk && onOk(JSON.parse(xhr.responseText)) }catch(e){ onOk && onOk({}) }
      }else{
        var msg = 'GET ' + path + ' 失败: ' + xhr.status + ' ' + xhr.responseText
        showError && showError(msg)
        onErr && onErr(xhr.status, xhr.responseText)
      }
    }
  }
  try{ xhr.send() }catch(e){
    try{ to.stop(); to.destroy() }catch(e2){}
    var msg = 'GET ' + path + ' 异常: ' + e
    showError && showError(msg)
    onErr && onErr(-1, String(e))
  }
}

function postJson(root, path, obj, onOk, onErr, showError){
  var xhr = new XMLHttpRequest()
  var timedOut = false
  var to = _makeTimer(root, timeoutMs, function(){
    timedOut = true
    try{ xhr.abort() }catch(e){}
    var msg = 'POST ' + path + ' 超时(' + timeoutMs + 'ms)'
    showError && showError(msg)
    onErr && onErr(408, msg)
  })
  xhr.open('POST', base + path)
  xhr.setRequestHeader('Content-Type', 'application/json')
  xhr.onreadystatechange = function(){
    if (xhr.readyState === XMLHttpRequest.DONE){
      try{ to.stop(); to.destroy() }catch(e){}
      if (timedOut) return
      if (xhr.status>=200 && xhr.status<300){
        try{ onOk && onOk(JSON.parse(xhr.responseText)) }catch(e){ onOk && onOk({}) }
      }else{
        var msg = 'POST ' + path + ' 失败: ' + xhr.status + ' ' + xhr.responseText
        showError && showError(msg)
        onErr && onErr(xhr.status, xhr.responseText)
      }
    }
  }
  try{ xhr.send(JSON.stringify(obj)) }catch(e){
    try{ to.stop(); to.destroy() }catch(e2){}
    var msg = 'POST ' + path + ' 异常: ' + e
    showError && showError(msg)
    onErr && onErr(-1, String(e))
  }
}

