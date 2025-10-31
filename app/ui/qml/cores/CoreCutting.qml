pragma Singleton
import QtQuick
import "../datas" as Datas

QtObject {
  id: root

  property var commands: []
  property int selectedIndex: -1
  property int activeIndex: -1
  property string runState: "IDLE"

  readonly property int displayIndex: {
    if (runState === "RUNNING" && activeIndex >= 0)
      return activeIndex
    if (selectedIndex >= 0)
      return selectedIndex
    return activeIndex >= 0 ? activeIndex : -1
  }

  readonly property var displayCommand: {
    var idx = root.displayIndex
    if (idx >= 0 && idx < commands.length)
      return commands[idx]
    return null
  }

  readonly property var displayImagePath: displayCommand && displayCommand.imagePath ? displayCommand.imagePath : []
  readonly property var displayRobotPath: displayCommand && displayCommand.robotPath ? displayCommand.robotPath : []

  function clear() {
    commands = []
    selectedIndex = -1
    activeIndex = -1
    runState = "IDLE"
    Datas.CodeDatas.lines = []
  }

  function loadProgram(rawData) {
    if (rawData === undefined || rawData === null) {
      return commands
    }
    var normalized = []
    var rawLines = rawData
    if (rawLines && rawLines.lines && Array.isArray(rawLines.lines))
      rawLines = rawLines.lines
    if (rawLines && rawLines.commands && Array.isArray(rawLines.commands))
      rawLines = rawLines.commands
    if (rawLines && rawLines.segments && Array.isArray(rawLines.segments))
      rawLines = rawLines.segments
    if (rawLines && rawLines.path_preview && Array.isArray(rawLines.path_preview))
      rawLines = rawLines.path_preview
    if (rawLines && rawLines.pathPreview && Array.isArray(rawLines.pathPreview))
      rawLines = rawLines.pathPreview

    if (!Array.isArray(rawLines) && Array.isArray(rawData))
      rawLines = rawData

    if (Array.isArray(rawLines)) {
      for (var i = 0; i < rawLines.length; ++i) {
        normalized.push(_normalizeCommand(rawLines[i], i))
      }
    }

    if (!normalized.length && rawData && typeof rawData === "object") {
      normalized.push(_normalizeCommand(rawData, 0))
    }

    commands = normalized
    Datas.CodeDatas.lines = normalized.map(function(item) { return item.displayText })
    if (runState === "RUNNING" && activeIndex >= 0)
      selectedIndex = -1
    else if (selectedIndex >= normalized.length)
      selectedIndex = normalized.length > 0 ? Math.max(0, Math.min(selectedIndex, normalized.length - 1)) : -1
    if (activeIndex >= normalized.length)
      activeIndex = normalized.length > 0 ? Math.min(activeIndex, normalized.length - 1) : -1
    return normalized
  }

  function updateRunState(state, currentIndex) {
    runState = state || "IDLE"
    var idx = Number(currentIndex)
    var newActive = (isNaN(idx) || idx < 0) ? -1 : idx
    activeIndex = newActive
    if (runState === "RUNNING" && newActive >= 0)
      selectedIndex = -1
  }

  function selectIndex(index) {
    if (runState === "RUNNING")
      return
    var idx = Number(index)
    if (isNaN(idx) || idx < 0 || idx >= commands.length)
      return
    selectedIndex = idx
  }

  function clearSelection() {
    selectedIndex = -1
  }

  // --- Helpers ----------------------------------------------------------------

  function _normalizeCommand(raw, index) {
    var entry = {
      index: index,
      raw: raw,
      displayText: "",
      type: "",
      start: null,
      end: null,
      maxDepth: undefined,
      cutDepth: undefined,
      cylinderAvoid: [],
      imagePath: [],
      robotPath: []
    }

    if (raw === undefined || raw === null) {
      entry.displayText = "-"
      return entry
    }

    if (typeof raw === "string") {
      entry.displayText = raw
      entry.type = ""
      return entry
    }

    if (typeof raw !== "object") {
      entry.displayText = String(raw)
      return entry
    }

    entry.displayText = _pickString(raw, [
      "display", "displayText", "label", "text", "command", "line", "title", "name"
    ])
    if (!entry.displayText || entry.displayText.length === 0)
      entry.displayText = _stringifySafely(raw)

    entry.type = _pickString(raw, [
      "type", "commandType", "mode", "operation", "category"
    ])

    var depthMax = _pickNumber(raw, ["maxDepth", "max_depth", "ZMaxRelDm", "zMaxRelDm"])
    if (depthMax !== undefined)
      entry.maxDepth = depthMax

    var depthCut = _pickNumber(raw, ["cutDepth", "cut_depth", "MxHeightCur", "mxHeightCur", "depth"])
    if (depthCut !== undefined)
      entry.cutDepth = depthCut

    var cylinders = raw.cylinderBypass !== undefined ? raw.cylinderBypass : raw.strQgNotSafe
    entry.cylinderAvoid = _normalizeCylinderList(cylinders)

    entry.imagePath = _normalizeImagePath(raw)
    entry.robotPath = _normalizeRobotPath(raw)

    var startPoint = raw.start !== undefined ? _normalizePoint(raw.start) : null
    var endPoint = raw.end !== undefined ? _normalizePoint(raw.end) : null
    if (!startPoint && entry.robotPath.length > 0)
      startPoint = _findPointByDef(entry.robotPath, 1) || entry.robotPath[0]
    if (!endPoint && entry.robotPath.length > 0)
      endPoint = _findPointByDef(entry.robotPath, 2) || entry.robotPath[entry.robotPath.length - 1]
    entry.start = startPoint
    entry.end = endPoint

    if (!entry.type || entry.type.length === 0) {
      entry.type = _inferTypeFromPoints(entry.robotPath, entry.cutDepth)
    }
    return entry
  }

  function _pickString(source, keys) {
    for (var i = 0; i < keys.length; ++i) {
      var key = keys[i]
      if (key in source && source[key] !== undefined && source[key] !== null) {
        var text = String(source[key]).trim()
        if (text.length > 0)
          return text
      }
    }
    return ""
  }

  function _pickNumber(source, keys) {
    for (var i = 0; i < keys.length; ++i) {
      var key = keys[i]
      if (key in source && source[key] !== undefined && source[key] !== null) {
        var num = Number(source[key])
        if (!isNaN(num))
          return num
      }
    }
    return undefined
  }

  function _normalizeCylinderList(value) {
    if (value === undefined || value === null)
      return []
    if (Array.isArray(value))
      return value.filter(function(item) { return item !== null && item !== undefined && item !== "" })
    var text = String(value).trim()
    if (text.length === 0)
      return []
    return text.split(/[;,]/).map(function(part) { return part.trim() }).filter(function(part) { return part.length > 0 })
  }

  function _normalizePoint(point) {
    if (!point || typeof point !== "object")
      return null
    var x = _pickNumber(point, ["x", "X", "fX"])
    var y = _pickNumber(point, ["y", "Y", "fY"])
    var z = _pickNumber(point, ["z", "Z", "fZ"])
    var result = {}
    if (x !== undefined) result.x = x
    if (y !== undefined) result.y = y
    if (z !== undefined) result.z = z
    return Object.keys(result).length ? result : null
  }

  function _normalizeImagePath(raw) {
    var pts = []
    var list = raw.imagePath
    if (!Array.isArray(list))
      list = raw.image_path
    if (!Array.isArray(list))
      list = raw.sListPPtsImage
    if (!Array.isArray(list))
      return pts

    for (var i = 0; i < list.length; ++i) {
      var item = list[i]
      if (!item)
        continue
      var x = _pickNumber(item, ["x", "X", "col", "Col", "fCol"])
      var y = _pickNumber(item, ["y", "Y", "row", "Row", "fRow"])
      if (x === undefined || y === undefined)
        continue
      pts.push({
        x: x,
        y: y,
        def: _pickNumber(item, ["iDef", "def", "role"])
      })
    }
    return pts
  }

  function _normalizeRobotPath(raw) {
    var pts = []
    var list = raw.robotPath
    if (!Array.isArray(list))
      list = raw.robot_path
    if (!Array.isArray(list))
      list = raw.sListPPtsRobot
    if (!Array.isArray(list))
      return pts

    for (var i = 0; i < list.length; ++i) {
      var item = list[i]
      var point = _normalizePoint(item)
      if (point) {
        var defValue = _pickNumber(item, ["iDef", "def", "role"])
        if (defValue !== undefined)
          point.def = defValue
        point.zMax = _pickNumber(item, ["ZMaxRelDm", "zMaxRelDm"])
        point.depth = _pickNumber(item, ["MxHeightCur", "mxHeightCur"])
        pts.push(point)
      }
    }
    return pts
  }

  function _stringifySafely(value) {
    try {
      var json = JSON.stringify(value)
      if (json && json.length > 80)
        json = json.slice(0, 77) + "..."
      return json || "-"
    } catch (err) {
      return "-"
    }
  }

  function _inferTypeFromPoints(points, depth) {
    if (depth !== undefined && !isNaN(Number(depth)) && Number(depth) > 0)
      return qsTr("切削")
    if (points && points.length > 1)
      return qsTr("移动")
    return qsTr("指令")
  }

  function _findPointByDef(path, defValue) {
    for (var i = 0; i < path.length; ++i) {
      if (path[i] && path[i].def === defValue)
        return path[i]
    }
    return null
  }
}
