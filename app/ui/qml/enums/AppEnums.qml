pragma Singleton
import QtQuick

QtObject {
  readonly property string title: "全自动 铜粒精密磨削系统"
  readonly property string companyName: "长沙铭准"
  readonly property string systemTitle: title

  readonly property var pageModels: ["实时", "手动", "调试", "测试"]
  readonly property var dataViewModels: ["2D", "3D"]
  readonly property var allRunModel: ["全自动", "半自动", "手动"]
  readonly property var allImageType: ["彩色", "灰度", "深度", "法线"]
}
