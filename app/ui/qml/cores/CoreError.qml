pragma Singleton
import QtQuick

Item {
    id: root
    // 全局错误弹窗是否可见
    property bool globErrorVisible: false
    // 全局错误提示文本
    property string globErrorText: ""

    // 显示错误信息
    function showError(msg) {
      root.globErrorText = msg
      root.globErrorVisible = true
    }

    // 清除错误信息
    function clear() {
      root.globErrorVisible = false
      root.globErrorText = ""
    }
}

