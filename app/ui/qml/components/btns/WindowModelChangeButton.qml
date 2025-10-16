import QtQuick

import "../../cores" as Cores

ColorItemDelegateButtonBase {
  tipText: qsTr("鍏ㄥ睆/鍙栨秷鍏ㄥ睆")
  height: parent.height
  width: height

  property bool shouMaxIcon: true

  source: shouMaxIcon
          ? Cores.CoreStyle.getIconSource("FullScreen.png")
          : Cores.CoreStyle.getIconSource("WindowScreen.png")
}
