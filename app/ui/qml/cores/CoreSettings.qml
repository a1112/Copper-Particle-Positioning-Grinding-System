pragma Singleton
import QtCore

Settings {
  id: uiSettings
  property string apiHost: "127.0.0.1"
  property int apiPort: 8010
  property int refreshMs: 120
}

