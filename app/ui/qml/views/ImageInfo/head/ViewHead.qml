import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


import "../../Base"
import "../../../cores" as Cores


BaseHead {

RowLayout{
  anchors.fill: parent
  Label { text: "视图"; color: Cores.CoreStyle.text; font.pixelSize: 14 }

  Item { Layout.fillWidth: true }

  ViewChiose{

  }

}

}
