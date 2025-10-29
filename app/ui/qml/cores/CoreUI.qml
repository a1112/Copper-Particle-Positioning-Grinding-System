pragma Singleton
import QtQuick
import "../enums" as Enums

Item {
    // 应用主标题，用于窗口标题栏显示
    property string title: Enums.AppEnums.title
    // 公司名称，供 UI 统一引用
    property string companyName: Enums.AppEnums.companyName
    // 系统名称，默认复用主标题
    property string systemTitle: Enums.AppEnums.systemTitle

    // 主页面标签名称列表
    property var pageModels: Enums.AppEnums.pageModels
    // 数据视图模式名称列表
    property var dataViewModels: Enums.AppEnums.dataViewModels
    // 所有运行模式名称
    property var allRunModel: Enums.AppEnums.allRunModel
    property var allImageType: Enums.AppEnums.allImageType
}
