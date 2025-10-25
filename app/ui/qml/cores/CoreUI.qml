pragma Singleton
import QtQuick

Item {
    // 主页面标签名称列表
    property var pageModels: ["实时", "手动", "调试", "测试"]
    // 数据视图模式名称列表
    property var dataViewModels: ["2D", "3D"]
    // 所有运行模式名称dataViewModels
    property var allRunModel: ["全自动", "半自动", "手动"]

    property var allImageType: ["彩色", "灰度","深度","法线"]
}
