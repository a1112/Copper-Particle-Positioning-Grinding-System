import QtQuick

import "../../cores" as Cores

ColorItemDelegateButtonBase {
  source: selected
          ? Cores.CoreStyle.getIconSource("qml/resource/icon/eye_l.png")
          : Cores.CoreStyle.getIconSource("qml/resource/icon/eyeu_l.png")
}
