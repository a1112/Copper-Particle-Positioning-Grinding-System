import QtQuick
import QtQuick.Window

Item {
  Shortcut { sequence: "Ctrl+E"; onActivated: estopDialog.open() }
  Shortcut { sequence: "Ctrl+Shift+E"; onActivated: estopDialog.open() }
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
