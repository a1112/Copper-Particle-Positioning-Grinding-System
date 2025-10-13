pragma Singleton
import QtQuick
/*

*/
Item {
    // ---- Theme palette ----
    // Name of active palette
    property string theme: "techBlueLight"

    property color titleColor: "#FFF"

    // Exposed colors (bind these in UI)
    property color primary: "#2563eb"
    property color accent: "#22d3ee"
    property color background: "#0b1220"
    property color surface: "#111827"
    property color text: "#e5e7eb"
    property color muted: "#94a3b8"
    // Status colors
    property color success: "#22c55e"
    property color warning: "#f59e0b"
    property color danger:  "#ef4444"
    property color info:    "#38bdf8"

    // Optional common accents
    property color border:  "#2a3441"
    property color overlay: "#00000080"

    property int CardHeadHeight: 25
    // Built‑in palettes
    readonly property var palettes: ({ techBlue: { primary: "#2563eb", accent: "#22d3ee", background: "#0b1220", surface: "#111827", text: "#e5e7eb", muted: "#94a3b8" }, techBlueLight: { primary: "#2563eb", accent: "#22d3ee", background: "#162337", surface: "#223047", text: "#f3f4f6", muted: "#b6c2cf" }, emerald: { primary: "#10b981", accent: "#34d399", background: "#0d1412", surface: "#121a16", text: "#e6f4ef", muted: "#9ca3af" }, amber: { primary: "#f59e0b", accent: "#f97316", background: "#141008", surface: "#1b1408", text: "#fff7ed", muted: "#fed7aa" }, nightPurple: { primary: "#8b5cf6", accent: "#a78bfa", background: "#0f0a1f", surface: "#15112b", text: "#ede9fe", muted: "#c4b5fd" }, graphite: { primary: "#64748b", accent: "#22c55e", background: "#0b0f14", surface: "#131922", text: "#e2e8f0", muted: "#94a3b8" } })

    function applyTheme(name){
        if (!name || !palettes[name]) return;
        theme = name;
        var p = palettes[name];
        primary = p.primary; accent = p.accent;
        background = p.background; surface = p.surface;
        text = p.text; muted = p.muted;
        // keep status colors constant across themes
        success = "#22c55e"; warning = "#f59e0b"; danger = "#ef4444"; info = "#38bdf8";
        border = "#3a4557"; overlay = "#00000066";
    }

    function getColor(key){
        // convenient lookup by string
        try { return this[key]; } catch(e) { return "transparent" }
    }

    Component.onCompleted: applyTheme(theme)
    // Normalize various forms into a valid qrc path.
    // Usage examples:
    //  getIconSource("share.png")                -> qrc:/resource/icon/share.png
    //  getIconSource("icon/share.png")           -> qrc:/resource/icon/share.png
    //  getIconSource("resource/icon/share.png")  -> qrc:/resource/icon/share.png
    //  getIconSource("qml/resource/icon/x.png")  -> qrc:/resource/icon/x.png
    //  getIconSource("qrc:/resource/icon/x.png") -> qrc:/resource/icon/x.png
    function getIconSource(name){
        if (!name || name.length===0)
            return "";
        // Already a qrc url
        if (name.indexOf("qrc:") === 0)
            return name;
        var p = String(name);
        // Strip leading ../ or .// and normalize
        p = p.replace(/^[.\/]+/, "");
        // Collapse backslashes just in case
        p = p.replace(/\\/g, "/");
        // Remove optional leading 'qml/'
        if (p.indexOf("qml/") === 0)
            p = p.substring(4);
        // If points into resource/ already
        if (p.indexOf("resource/") === 0)
            return "qrc:/" + p;
        // Allow passing subdir like 'icon/xxx.png'
        if (p.indexOf("icon/") === 0)
            return "qrc:/resource/" + p;
        // Fall back to icon folder for bare filenames
        return "qrc:/resource/icon/" + p;
    }
}


