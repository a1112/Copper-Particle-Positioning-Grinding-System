pragma Singleton
import QtQuick

QtObject {
  id: root
  property bool connected: false
  property string runState: "IDLE"
  property int currentIndex: -1
  property var lines: []
  property var entries: []
  property alias model: internalModel

  ListModel { id: internalModel }

  function reset() {
    connected = false
    runState = "IDLE"
    currentIndex = -1
    clearProgram()
  }

  function setProgramList(list) {
    model.clear()
    var source = Array.isArray(list) ? list : []
    var normalized = []
    var texts = []
    for (var i = 0; i < source.length; ++i) {
      var item = source[i]
      var text = "-"
      if (item && item.displayText !== undefined)
        text = String(item.displayText)
      else if (item && item.text !== undefined)
        text = String(item.text)
      else if (item && item.command !== undefined)
        text = String(item.command)
      else if (item !== undefined && item !== null)
        text = String(item)

      var entryObj
      if (item && typeof item === "object")
        entryObj = item
      else
        entryObj = { displayText: text }
      entryObj.displayText = text
      entryObj.index = entryObj.index !== undefined ? entryObj.index : (i + 1)
      normalized.push(entryObj)
      texts.push(text)
      model.append({ idx: i + 1, text: text, status: "READY" })
    }
    entries = normalized
    lines = texts
    updateStatuses()
  }

  function clearProgram() {
    model.clear()
    entries = []
    lines = []
  }

  function updateStatuses() {
    if (!model || model.count === undefined)
      return
    var cur = currentIndex
    var state = runState
    for (var i = 0; i < model.count; ++i) {
      var status = "READY"
      if (cur >= 0) {
        if (i === cur) {
          if (state === "ERROR")
            status = "FAIL"
          else if (state === "RUNNING")
            status = "RUNNING"
          else
            status = "READY"
        } else if (i < cur) {
          status = "OK"
        }
      }
      model.setProperty(i, "status", status)
      if (entries && entries.length > i && entries[i] && typeof entries[i] === "object")
        entries[i].status = status
    }
  }

  onCurrentIndexChanged: updateStatuses()
  onRunStateChanged: updateStatuses()


}
