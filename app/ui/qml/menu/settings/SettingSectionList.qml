import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: root
    property string title: ""
    property var sections: [] // [{ name: string, items: [{key, value, description}] }]

    spacing: 8
    Layout.fillWidth: true

    // Title
    Label {
        text: root.title
        visible: (text && text.length > 0)
        color: "#9ad"
        font.bold: true
        Layout.fillWidth: true
    }

    Repeater {
        model: Array.isArray(root.sections) ? root.sections : []
        delegate: ColumnLayout {
            spacing: 4
            Layout.fillWidth: true

            // Section header
            Label {
                text: (modelData && modelData.name) ? String(modelData.name) : ""
                color: "#cbd5e1"
                font.bold: true
                Layout.fillWidth: true
            }

            // Items grid
            ColumnLayout {
                Layout.fillWidth: true
                Repeater {
                    model: (modelData && Array.isArray(modelData.items)) ? modelData.items : []
                    delegate: Rectangle {
                        Layout.fillWidth: true
                        width: parent ? parent.width : 800
                        height: Math.max(28, txtKey.implicitHeight)
                        color: index % 2 === 0 ? "#141821" : "#171d27"
                        radius: 4
                        border.color: "#232a36"

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 6
                            spacing: 10
                            Label {
                                id: txtKey
                                text: (modelData && modelData.key) ? String(modelData.key) : ""
                                color: "#e2e8f0"
                                Layout.preferredWidth: 240
                                elide: Text.ElideRight
                            }
                            Label {
                                text: (modelData && modelData.value) ? String(modelData.value) : "-"
                                color: "#cbd5e1"
                                Layout.preferredWidth: 200
                                elide: Text.ElideRight
                            }
                            Label {
                                text: (modelData && modelData.description) ? String(modelData.description) : ""
                                color: "#94a3b8"
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                                maximumLineCount: 3
                            }
                        }
                    }
                }
            }
        }
    }
}

