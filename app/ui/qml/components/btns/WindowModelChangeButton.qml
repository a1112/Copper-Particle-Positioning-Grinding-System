import QtQuick

import "../../cores" as Cores

ColorItemDelegateButtonBase {
  tipText: qsTr("\u5168\u5c4f/\u53d6\u6d88\u5168\u5c4f")
  height: parent.height
  width: height

  property bool shouMaxIcon: true

  source: shouMaxIcon
          ? Cores.CoreStyle.getIconSource("FullScreen.png")
          : Cores.CoreStyle.getIconSource("WindowScreen.png")
}
