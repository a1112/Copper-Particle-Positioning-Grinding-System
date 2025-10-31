pragma Singleton
import QtQuick
import "../Api" as Api
import "../datas" as Datas

QtObject {
  // 标定数据获取任务
  id: root

  // 启动时立即刷新一次
  function start() {
    refresh()
  }

  // 调用后端接口同步最新标定参数
  function refresh() {
    Api.ApiClient.calibration(function(payload) {
      Datas.CalibrationData.applySnapshot(payload)
    }, function(status, message) {
      console.warn("CalibrationWork refresh error", status, message)
    })
  }
}
