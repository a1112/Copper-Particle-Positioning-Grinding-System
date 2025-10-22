pragma Singleton
import QtQuick

Item {
    // 主页面标签名称列表
    property var pageModels: ["实时", "手动", "调试", "测试"]
    // 数据视图模式名称列表
    property var dataViewModels: ["深度图", "3D"]
    // 所有运行模式名称
    property var allRunModel: ["全自动", "半自动", "手动"]
}
