import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "head"
import "main"
import "foot"

ColumnLayout {
  id: root
  spacing: 2

  HeadView { Layout.fillWidth: true; Layout.preferredHeight: 50 }

  MainPages { Layout.fillWidth: true; Layout.fillHeight: true }

  FootView { Layout.fillWidth: true; Layout.preferredHeight: 25 }
}
