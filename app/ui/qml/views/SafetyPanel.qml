import QtQuick
import QtQuick.Controls

Item {
  id: root
  Column {
    spacing: 4
    Label { text: "安全互锁"; font.bold: true }
    Row { spacing: 12
      Label { text: "门禁:" + (backend.lockDoor ? 'OK' : 'NG') }
      Label { text: "真空:" + (backend.lockVacuum ? 'OK' : 'NG') }
      Label { text: "急停:" + (backend.lockEStop ? 'OK' : 'NG') }
      Label { text: "回零:" + (backend.lockHomed ? 'OK' : 'NG') }
      Label { text: "主轴就绪:" + (backend.lockSpindle ? 'OK' : 'NG') }
    }
  }
}

