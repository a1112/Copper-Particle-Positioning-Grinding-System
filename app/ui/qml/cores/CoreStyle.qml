pragma Singleton
import QtQuick

Item {
    // 当前启用的主题名称
    property string theme: "techBlueLight"
    // 标题文字默认颜色
    property color titleColor: "#FFF"

    // 主题主色调
    property color primary: "#2563eb"
    // 主题强调色
    property color accent: "#22d3ee"
    // 应用背景色
    property color background: "#0b1220"
    // 常规卡片背景色
    property color surface: "#111827"
    // 正文字体颜色
    property color text: "#e5e7eb"
    // 次要文字颜色
    property color muted: "#94a3b8"

    // 状态：成功/警告/危险/提示
    property color success: "#22c55e"
    property color warning: "#f59e0b"
    property color danger:  "#ef4444"
    property color info:    "#38bdf8"

    // 辅助边框色
    property color border:  "#2a3441"
    // 遮罩层颜色
    property color overlay: "#00000080"

    // 预置调色板集合
    readonly property var palettes: ({
        techBlue:       { primary: "#2563eb", accent: "#22d3ee", background: "#0b1220", surface: "#111827", text: "#e5e7eb", muted: "#94a3b8" },
        techBlueLight:  { primary: "#2563eb", accent: "#22d3ee", background: "#162337", surface: "#223047", text: "#f3f4f6", muted: "#b6c2cf" },
        emerald:        { primary: "#10b981", accent: "#34d399", background: "#0d1412", surface: "#121a16", text: "#e6f4ef", muted: "#9ca3af" },
        amber:          { primary: "#f59e0b", accent: "#f97316", background: "#141008", surface: "#1b1408", text: "#fff7ed", muted: "#fed7aa" },
        nightPurple:    { primary: "#8b5cf6", accent: "#a78bfa", background: "#0f0a1f", surface: "#15112b", text: "#ede9fe", muted: "#c4b5fd" },
        graphite:       { primary: "#64748b", accent: "#22c55e", background: "#0b0f14", surface: "#131922", text: "#e2e8f0", muted: "#94a3b8" }
    })

    // 根据名称应用主题色
    function applyTheme(name){
        if (!name) return;
        if (!palettes[name]) return;
        theme = name;
        var p = palettes[name];
        primary = p.primary; accent = p.accent;
        background = p.background; surface = p.surface;
        text = p.text; muted = p.muted;
        // 状态类颜色保持不变
        success = "#22c55e"; warning = "#f59e0b"; danger = "#ef4444"; info = "#38bdf8";
        border = "#3a4557"; overlay = "#00000066";
    }

    // 通过键名获取对应颜色
    function getColor(key){
        try { return this[key]; } catch(e) { return "transparent" }
    }

    Component.onCompleted: applyTheme(theme)

    // 归一化图标资源路径
    // 传入示例：
    //  getIconSource("share.png")                -> qrc:/resource/icon/share.png
    //  getIconSource("icon/share.png")           -> qrc:/resource/icon/share.png
    //  getIconSource("resource/icon/share.png")  -> qrc:/resource/icon/share.png
    //  getIconSource("qml/resource/icon/x.png")  -> qrc:/resource/icon/x.png
    //  getIconSource("qrc:/resource/icon/x.png") -> qrc:/resource/icon/x.png
    function getIconSource(name){
        if (!name)
            return "";
        if (name.length===0)
            return "";
        if (name.indexOf("qrc:") === 0)
            return name;
        var p = String(name);
        p = p.replace(/^[.\/]+/, "");
        p = p.replace(/\\/g, "/");
        if (p.indexOf("qml/") === 0)
            p = p.substring(4);
        if (p.indexOf("resource/") === 0)
            return "qrc:/" + p;
        if (p.indexOf("icon/") === 0)
            return "qrc:/resource/" + p;
        return "qrc:/resource/icon/" + p;
    }

    // 卡片标题区域高度
    property int cardHeadHeight: 30
    // 顶部下拉框高度
    property int headComboBoxHeigh: 30
    // 顶部数值框高度
    property int headSpinBoxHeigh: 30
}
