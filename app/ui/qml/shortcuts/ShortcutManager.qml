pragma Singleton
import QtQuick
import QtQuick.Controls

// Minimal shortcut manager singleton.
// Provides a hook to attach common global shortcuts when desired.
QtObject {
  id: shortcutManager

  // Root window to attach shortcuts to (optional)
  property var rootWindow

  // Example signals that pages may listen to
  signal openTestPage()
  signal toggleFullscreen()

  // Consumers can bind shortcuts in their QML directly.
  // This singleton primarily serves as a central place to share intent.
}

