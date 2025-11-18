pragma Singleton
import QtCore

Settings {
  id: uiSettings
  // API 服务主机地址
  property string apiHost: "127.0.0.1"
  // API 服务端口
  property int apiPort: 8010
  // UI 自动刷新间隔（毫秒）
  property int refreshMs: 120
  // 默认界面语言
  property string language: "zh_CN"
  property real fontScale: 1.0

  // 参数设置中心缓存页签索引
  property int parameterTabIndex: 0
  // 参数设置中心缓存数据
  property var parameterGeneral: ({})
  property var parameterProcess: ({})
  property var parameterAlgorithm: ({})
  property var parameterAuto: ({})
  property var parameterTools: []
}
