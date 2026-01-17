import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../../../cores" as Cores

// 机器人控制面板 - 用于控制机械臂的各个关节
Pane {
  id: root

  // 输入值属性
  property int rotation1Value: 0
  property int rotation2Value: 45
  property int rotation3Value: 45
  property int rotation4Value: 0
  property bool clawsOpen: true

  // 信号
  signal rotation1Changed(int value)
  signal rotation2Changed(int value)
  signal rotation3Changed(int value)
  signal rotation4Changed(int value)
  signal clawsToggled(bool open)
  signal resetClicked()

  padding: 12

  background: Rectangle {
    color: Qt.rgba(0.1, 0.12, 0.16, 0.85)
    border.color: Cores.CoreStyle.border
    border.width: 1
    radius: 8
  }

  ColumnLayout {
    spacing: 10
    anchors.fill: parent

    // 标题
    Label {
      text: qsTr("机器人控制")
      font.bold: true
      font.pixelSize: 14
      color: Cores.CoreStyle.text
      Layout.fillWidth: true
    }

    // 分隔线
    Rectangle {
      Layout.fillWidth: true
      Layout.preferredHeight: 1
      color: Cores.CoreStyle.border
    }

    // Rotation 1 - 手腕旋转
    LabeledSlider {
      labelText: qsTr("手腕")
      sliderWidth: 140
      from: -90
      to: 90
      value: root.rotation1Value
      onValueEdited: root.rotation1Changed(Math.round(value))
    }

    // Rotation 2 - 手臂旋转
    LabeledSlider {
      labelText: qsTr("大臂")
      sliderWidth: 140
      from: -135
      to: 135
      value: root.rotation2Value
      onValueEdited: root.rotation2Changed(Math.round(value))
    }

    // Rotation 3 - 前臂旋转
    LabeledSlider {
      labelText: qsTr("小臂")
      sliderWidth: 140
      from: -90
      to: 90
      value: root.rotation3Value
      onValueEdited: root.rotation3Changed(Math.round(value))
    }

    // Rotation 4 - 基座旋转
    LabeledSlider {
      labelText: qsTr("基座")
      sliderWidth: 140
      from: -180
      to: 180
      value: root.rotation4Value
      onValueEdited: root.rotation4Changed(Math.round(value))
    }

    // 爪子开关
    RowLayout {
      Layout.fillWidth: true
      spacing: 8

      Label {
        text: qsTr("爪子")
        color: Cores.CoreStyle.text
        font.pixelSize: 12
      }

      Switch {
        checked: root.clawsOpen
        text: checked ? qsTr("张开") : qsTr("闭合")
        onToggled: root.clawsToggled(checked)
      }
    }

    // 分隔线
    Rectangle {
      Layout.fillWidth: true
      Layout.preferredHeight: 1
      color: Cores.CoreStyle.border
    }

    // 预设姿势按钮
    RowLayout {
      Layout.fillWidth: true
      spacing: 6

      Button {
        text: "Pose 1"
        Layout.preferredWidth: 55
        Layout.preferredHeight: 32
        font.pixelSize: 11
        onClicked: {
          root.rotation1Changed(30)
          root.rotation2Changed(60)
          root.rotation3Changed(90)
          root.rotation4Changed(145)
        }
      }

      Button {
        text: "Pose 2"
        Layout.preferredWidth: 55
        Layout.preferredHeight: 32
        font.pixelSize: 11
        onClicked: {
          root.rotation1Changed(60)
          root.rotation2Changed(45)
          root.rotation3Changed(45)
          root.rotation4Changed(60)
        }
      }

      Button {
        text: qsTr("复位")
        Layout.preferredWidth: 55
        Layout.preferredHeight: 32
        font.pixelSize: 11
        onClicked: root.resetClicked()
      }
    }
  }

  // 带标签的滑块组件
  component LabeledSlider: RowLayout {
    property string labelText: ""
    property real sliderWidth: 120
    property alias from: slider.from
    property alias to: slider.to
    property alias value: slider.value

    signal valueEdited(real value)

    spacing: 6

    Label {
      text: labelText
      color: Cores.CoreStyle.text
      font.pixelSize: 11
      Layout.preferredWidth: 35
    }

    Slider {
      id: slider
      Layout.preferredWidth: sliderWidth
      implicitHeight: 20
      onMoved: parent.valueEdited(value)
    }

    Label {
      text: Math.round(parent.value).toString()
      color: Cores.CoreStyle.muted
      font.pixelSize: 10
      Layout.preferredWidth: 28
      horizontalAlignment: Text.AlignRight
    }
  }
}
