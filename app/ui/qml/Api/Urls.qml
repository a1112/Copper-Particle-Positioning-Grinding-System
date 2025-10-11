pragma Singleton
import QtQuick
import "../cores" as Cores

QtObject {
  // Host and port from CoreSettings
  property string host: Cores.CoreSettings.apiHost
  property int port: Cores.CoreSettings.apiPort

  function base() {
    return 'http://' + Cores.CoreSettings.apiHost + ':' + Cores.CoreSettings.apiPort
  }
  function api(path) {
    if (!path) path = ''
    if (path.length>0 && path[0] !== '/') path = '/' + path
    return base() + path
  }
  function ws() {
    return 'ws://' + Cores.CoreSettings.apiHost + ':' + Cores.CoreSettings.apiPort + '/ws'
  }
  function docs() { return base() + '/docs' }
}
