import QtQuick

Item{

    // Global shortcuts: Ctrl+E / Ctrl+Shift+E -> open E-STOP confirmation; Enter/Return to confirm
    Shortcut { sequence: "Ctrl+E"; onActivated: estopDialog.open() }
    Shortcut { sequence: "Ctrl+Shift+E"; onActivated: estopDialog.open() }
    Shortcut { sequence: "Enter"; onActivated: if (estopDialog.visible) estopDialog.accept() }
    Shortcut { sequence: "Return"; onActivated: if (estopDialog.visible) estopDialog.accept() }


}
