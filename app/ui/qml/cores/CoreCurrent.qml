pragma Singleton
import QtQuick

QtObject {
  id: root

  property int historyLimit: 50
  property double lastUpdatedMs: 0

  property var workpiece: ({
    id: 0,
    code: "",
    type: "",
    material: ""
  })

  property var record: ({
    id: 0,
    status: ""
  })

  property var task: ({
    name: "",
    status: ""
  })

  property var lastControl: ({})
  property var controlHistory: []

  function reset() {
    workpiece = {
      id: 0,
      code: "",
      type: "",
      material: ""
    }
    record = {
      id: 0,
      status: ""
    }
    task = {
      name: "",
      status: ""
    }
    lastControl = {}
    controlHistory = []
    lastUpdatedMs = Date.now()
  }

  function updateWorkpiece(info) {
    if (!info)
      return
    workpiece = _merge(workpiece, info)
    lastUpdatedMs = Date.now()
  }

  function updateRecord(info) {
    if (!info)
      return
    record = _merge(record, info)
    lastUpdatedMs = Date.now()
  }

  function updateTask(info) {
    if (!info)
      return
    task = _merge(task, info)
    lastUpdatedMs = Date.now()
  }

  function pushControl(action, params, metadata) {
    var entry = {
      action: action || "",
      params: params ? _clone(params) : {},
      metadata: metadata ? _clone(metadata) : {},
      ts: Date.now()
    }
    var history = Array.isArray(controlHistory) ? controlHistory.slice(0) : []
    history.unshift(entry)
    if (history.length > historyLimit)
      history.length = historyLimit
    controlHistory = history
    lastControl = entry
    lastUpdatedMs = entry.ts
  }

  function _merge(target, source) {
    var base = (target && typeof target === "object") ? _clone(target) : {}
    var src = (source && typeof source === "object") ? _clone(source) : {}
    for (var key in src) {
      if (!src.hasOwnProperty(key))
        continue
      base[key] = src[key]
    }
    return base
  }

  function _clone(value) {
    if (value === null || value === undefined)
      return {}
    if (Array.isArray(value))
      return value.slice(0)
    if (typeof value !== "object")
      return value
    try {
      return JSON.parse(JSON.stringify(value))
    } catch (err) {
      var result = {}
      for (var key in value) {
        if (!value.hasOwnProperty(key))
          continue
        result[key] = value[key]
      }
      return result
    }
  }
}
