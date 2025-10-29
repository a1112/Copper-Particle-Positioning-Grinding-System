pragma Singleton
import QtQuick
import "../enums" as Enums

Item {
    // 主页面标签名称列表
    property var pageModels: Enums.AppEnums.pageModels
    // 数据视图模式名称列表
    property var dataViewModels: Enums.AppEnums.dataViewModels
    // 所有运行模式名称
    property var allRunModel: Enums.AppEnums.allRunModel
    property var allImageType: Enums.AppEnums.allImageType
}

