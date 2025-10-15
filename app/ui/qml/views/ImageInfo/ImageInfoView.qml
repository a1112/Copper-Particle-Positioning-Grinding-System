import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "head"
import "../../Sockets" as Sockets
import "../../Api" as Api
import "../Base"
import "../../cores" as Cores
import "../../components/btns" as Btns

import "View2D"
BaseCard {
  id: root
  property int refreshMs: 150


  property var pathPoints: []
  readonly property int maxPath: 2000

  ColumnLayout {
    anchors.fill: parent
    anchors.margins: 8
    spacing: 6
    ViewHead{}
    StackLayout{

      View2D{}


    }
  }
}

