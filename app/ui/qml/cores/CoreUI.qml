pragma Singleton
import QtQuick

Item {
    // 应用主标题，用于窗口标题栏显示
    property string title: "全自动 铜粒精密磨削系统"
    // 公司名称，供 UI 统一引用
    property string companyName: "长沙铭准"
    // 系统名称，默认复用主标题
    property string systemTitle: title

    // 主页面标签名称列表
    property var pageModels: ["实时", "手动", "调试", "测试"]
    // 数据视图模式名称列表
    property var dataViewModels: ["2D", "3D"]
    // 所有运行模式名称dataViewModels
    property var allRunModel: ["全自动", "半自动", "手动"]

    property var allImageType: ["彩色", "灰度","深度","法线"]
}
