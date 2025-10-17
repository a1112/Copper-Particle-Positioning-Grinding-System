pragma Singleton
import QtQuick
import "../cores" as Core
QtObject {
  // Basic identifiers/state exposed to the UI
  property string serialNumber: "-"
  property string runMode: Core.CoreState.currentRunModelName
  property string runState:"-"
}
