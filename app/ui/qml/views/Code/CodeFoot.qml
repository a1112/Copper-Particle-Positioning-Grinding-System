import QtQuick
import QtQuick.Controls.Material
import QtQuick.Layouts
import QtCore

import "../../cores" as Cores

RowLayout {
  id: root
  spacing: 8

  // Text area whose content length is displayed.
  property Item editorItem: null

  Label {
    text: (root.editorItem && root.editorItem.text !== undefined)
          ? root.editorItem.text.length + qsTr(" chars")
          : "-"
    color: Cores.CoreStyle.muted
  }
}
