import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../cores" as Cores
import "../Api" as Api
import "../works" as Works

Dialog {
  id: dataDialog
  title: qsTr("手动添加工件")
  modal: true
  standardButtons: Dialog.Cancel
  focus: true
  property bool busy: false

  width: 420

  onRejected: {
    busy = false
  }

  function resetForm() {
    tfCode.text = ""
    tfType.text = "DEMO"
    tfMaterial.text = "Copper"
    tfDimensions.text = "100x100x10"
    tfSurface.text = "Ra <= 0.2"
    tfRoughness.text = ""
  }

  function openWithReset() {
    resetForm()
    open()
  }

  function submit() {
    if (busy)
      return
    busy = true
    var payload = {
      code: tfCode.text,
      type: tfType.text,
      material: tfMaterial.text,
      dimensions: tfDimensions.text,
      surface_requirement: tfSurface.text,
      roughness_required: tfRoughness.text
    }
    Api.ApiClient.post("/data/workpieces", payload, function(response) {
      busy = false
      Works.TaskWork.refresh()
      if (response && response.workpiece)
        console.log("workpiece created", response.workpiece.id)
      dataDialog.close()
    }, function(_, message) {
      busy = false
      Cores.CoreError.showError(message || qsTr("保存失败"))
    })
  }

  contentItem: ColumnLayout {
    spacing: 10
    anchors.fill: parent
    anchors.margins: 16

    TextField {
      id: tfCode
      placeholderText: qsTr("工件编号 (留空自动生成)")
      enabled: !dataDialog.busy
    }

    TextField {
      id: tfType
      placeholderText: qsTr("工件类型")
      enabled: !dataDialog.busy
    }

    TextField {
      id: tfMaterial
      placeholderText: qsTr("材料")
      enabled: !dataDialog.busy
    }

    TextField {
      id: tfDimensions
      placeholderText: qsTr("尺寸 (例如 100x100x10)")
      enabled: !dataDialog.busy
    }

    TextField {
      id: tfSurface
      placeholderText: qsTr("表面要求")
      enabled: !dataDialog.busy
    }

    TextField {
      id: tfRoughness
      placeholderText: qsTr("要求粗糙度 (数值)")
      inputMethodHints: Qt.ImhFormattedNumbersOnly
      enabled: !dataDialog.busy
    }
  }

  footer: DialogButtonBox {
    spacing: 8
    alignment: Qt.AlignRight
    Button {
      text: qsTr("保存")
      enabled: !dataDialog.busy
      onClicked: dataDialog.submit()
    }
    Button {
      text: qsTr("取消")
      enabled: !dataDialog.busy
      onClicked: dataDialog.close()
    }
  }
}
