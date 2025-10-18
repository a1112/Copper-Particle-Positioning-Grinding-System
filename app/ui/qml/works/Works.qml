pragma Singleton
import QtQuick
import "." as WorksModule

QtObject {
  function startAll() {
    WorksModule.StatusWork.start()
    WorksModule.LogsWork.start()
    WorksModule.CodeWork.start()
    WorksModule.CuttingWork.start()
    WorksModule.DeviceInfoWork.start()
  }
}
