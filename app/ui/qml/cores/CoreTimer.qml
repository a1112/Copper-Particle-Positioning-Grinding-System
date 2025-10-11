pragma Singleton
import QtQuick

Item {
  id: root
  // Export a ticking timestamp for latency calculations
  property double nowTs: 0

  Timer { interval: 500; running: true; repeat: true; onTriggered: root.nowTs = Date.now() }
}

