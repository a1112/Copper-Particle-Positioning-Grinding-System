pragma Singleton
import QtQuick

Item {
  id: root
  // 导出实时时间戳，用于延迟计算等用途
  property double nowTs: 0

  // 定时刷新时间戳，保持界面数据实时
  Timer { interval: 500; running: true; repeat: true; onTriggered: root.nowTs = Date.now() }
}

