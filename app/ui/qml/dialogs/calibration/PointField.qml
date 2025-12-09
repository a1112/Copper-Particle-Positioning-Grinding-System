import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components/Base"

RowLayout {
  id: root
  property string key: ""
  property alias labelText: label.text
  property alias field: input
  Label {
    id: label
    color: "#cbd5e1"
  }

  TextFieldBase {
    id: input
  }
}
