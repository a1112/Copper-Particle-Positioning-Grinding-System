pragma Singleton
import QtQuick

QtObject {
  id: root
  property bool connected: false
  property string runState: "IDLE"
  property int currentIndex: -1
  property var lines: []

  function reset() {
    connected = false
    runState = "IDLE"
    currentIndex = -1
    lines = []
  }
}
