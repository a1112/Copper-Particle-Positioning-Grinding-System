import QtQuick

import "../../cores" as Cores

ImageButton {
  source: Cores.CoreStyle.getIconSource("flush.png")

  Item {
    anchors.fill: parent

    Image {
      id: image
      anchors.fill: parent
      fillMode: Image.PreserveAspectFit
    }
  }
}

