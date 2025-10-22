pragma Singleton
import QtQuick

Item {
    // 应用主标题，用于窗口标题栏显示
    property string title: "全自动 铜粒精密磨削系统"
    // 公司名称，供 UI 统一引用
    property string companyName: "长沙铭准"
    // 系统名称，默认复用主标题
    property string systemTitle: title
}
