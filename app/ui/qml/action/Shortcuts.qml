import QtQuick
import QtQuick.Window
import "../cores" as Cores

Item {
  function triggerEstopShortcut() {
    if (Cores.CoreControl.requireEstopConfirmation)
      estopDialog.open()
    else
      Cores.CoreControl.estop()
  }

  Shortcut { sequence: "Ctrl+E"; onActivated: triggerEstopShortcut() }
  Shortcut { sequence: "Ctrl+Shift+E"; onActivated: triggerEstopShortcut() }
  Shortcut { sequence: "Enter"; onActivated: if (estopDialog.visible) estopDialog.accept() }
  Shortcut { sequence: "Return"; onActivated: if (estopDialog.visible) estopDialog.accept() }
  Shortcut {
    sequence: "F11"
    onActivated: {
      if (rootWindow.visibility === Window.FullScreen) {
        rootWindow.showMaximized()
      } else {
        rootWindow.showFullScreen()
      }
    }
  }

  Shortcut {
    sequence: "F12"
    onActivated: {
      testWindow.visible=true
    }
  }
}
