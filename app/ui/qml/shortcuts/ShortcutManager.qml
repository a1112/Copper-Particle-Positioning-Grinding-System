import QtQuick
import QtQuick.Window

Item {
  id: manager
  // Root window reference for toggling full screen
  property var rootWindow
  signal openTestPage()

  // F11: toggle fullscreen
  Shortcut {
    sequence: "F11"
    onActivated: {
      if (!manager.rootWindow) return;
      var vis = manager.rootWindow.visibility;
      manager.rootWindow.visibility = (vis === Window.FullScreen) ? Window.Windowed : Window.FullScreen;
    }
  }
  // F12: open test page dialog
  Shortcut {
    sequence: "F12"
    onActivated: manager.openTestPage()
  }
}
