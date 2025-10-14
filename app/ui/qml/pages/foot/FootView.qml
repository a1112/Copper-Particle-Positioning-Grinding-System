import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../Sockets" as Sockets
import "../../cores" as Cores
import "../../Api" as Api
import "../../components/btns" as Btns
Item {
  Layout.fillWidth: true
  height: 30

  Frame { anchors.fill: parent }

  RowLayout {
    anchors.fill: parent
    spacing: 12


    Item{
      Layout.fillWidth: true
      height: 1
    }

    ViewMangeRow{
    }

    PingLabel{}

    Btns.CheckDelegateBase{
    }

    Item{
      width: 15
      height: 1
    }

  }
}



