import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../cores" as Cores

// Digital clock using DS-DIGIT.TTF, with date + time and color controls
Item {
  id: root
  implicitHeight: 30
  implicitWidth: 180

  // Font and colors
  property int timePixelSize: 26
  property int datePixelSize: 15
  property color timeColor: Cores.CoreStyle.accent
  property color dateColor: Cores.CoreStyle.muted
  property color outlineColor: Cores.CoreStyle.border

  // Formats
  property string timeFormat: "HH:mm:ss"
  property string dateFormat: "yyyy-MM-dd"
  property bool showDate: true

  // Exposed values
  property string currentTime: "--:--:--"
  property string currentDate: "----/--/--"

  FontLoader { id: ds; source: "qrc:/resource/font/DS-DIGIT.TTF" }

  function pad2(n){ return (n<10?('0'+n):(''+n)) }
  function fmtDate(d, f){
    var Y = d.getFullYear();
    var M = pad2(d.getMonth()+1);
    var D = pad2(d.getDate());
    var H = pad2(d.getHours());
    var m = pad2(d.getMinutes());
    var s = pad2(d.getSeconds());
    return f.replace('yyyy', Y).replace('MM', M).replace('dd', D).replace('HH', H).replace('mm', m).replace('ss', s)
  }

  function refresh(){
    var d = new Date();
    currentTime = fmtDate(d, timeFormat);
    currentDate = fmtDate(d, dateFormat);
  }

  Timer { interval: 500; running: true; repeat: true; onTriggered: refresh() }
  Component.onCompleted: refresh()

  Row {
    anchors.fill: parent
    spacing: 8
    // Date (left)
    Text {
      visible: root.showDate
      text: root.currentDate
      font.family: ds.name || 'DS-DIGIT'
      font.pixelSize: root.datePixelSize
      color: root.dateColor
      verticalAlignment: Text.AlignVCenter
      style: Text.Outline
      styleColor: root.outlineColor
    }
    // Time (right)
    Text {
      text: root.currentTime
      font.family: ds.name || 'DS-DIGIT'
      font.pixelSize: root.timePixelSize
      color: root.timeColor
      verticalAlignment: Text.AlignVCenter
      style: Text.Outline
      styleColor: root.outlineColor
    }
  }
}
