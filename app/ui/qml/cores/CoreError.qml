import QtQuick

Item {
    id: root
    // Properly typed state for global error dialog
    property bool globErrorVisible: false
    property string globErrorText: ""

    function showError(msg) {
      root.globErrorText = msg
      root.globErrorVisible = true
    }

    function clear() {
      root.globErrorVisible = false
      root.globErrorText = ""
    }
}
