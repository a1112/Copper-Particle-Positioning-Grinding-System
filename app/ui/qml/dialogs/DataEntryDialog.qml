import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../cores" as Cores
import "../Api" as Api
import "../works" as Works

Dialog {
  id: dataDialog
  title: qsTr("工件数据管理")
  modal: true
  standardButtons: Dialog.Cancel
  focus: true
  property bool busy: false
  property bool listBusy: false
  property int fetchLimit: 20

  width: 540

  onRejected: {
    busy = false
    listBusy = false
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
    refreshWorkpieces()
    open()
  }

  ListModel {
    id: workpieceModel
  }

  function refreshWorkpieces() {
    if (listBusy)
      return
    listBusy = true
    Api.ApiClient.get("/data/workpieces?limit=" + fetchLimit, function(response) {
      workpieceModel.clear()
      var rows = response && response.workpieces ? response.workpieces : []
      for (var i = 0; i < rows.length; i++) {
        var row = rows[i] || {}
        workpieceModel.append({
          workpieceId: row.id,
          code: row.code || "",
          type: row.type || "",
          material: row.material || "",
          dimensions: row.dimensions || "",
          surface: row.surface_requirement || "",
          roughness: row.roughness_required !== null && row.roughness_required !== undefined ? row.roughness_required : "",
          createdAt: row.created_time || ""
        })
      }
      listBusy = false
    }, function(_, message) {
      listBusy = false
      if (message)
        Cores.CoreError.showError(message)
    })
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
      refreshWorkpieces()
      if (response && response.workpiece)
        console.log("workpiece created", response.workpiece.id)
      dataDialog.close()
    }, function(_, message) {
      busy = false
      Cores.CoreError.showError(message || qsTr("保存失败"))
    })
  }

  function deleteWorkpiece(workpieceId) {
    if (busy || !workpieceId)
      return
    busy = true
    Api.ApiClient.del("/data/workpieces/" + workpieceId, function() {
      busy = false
      refreshWorkpieces()
    }, function(_, message) {
      busy = false
      Cores.CoreError.showError(message || qsTr("删除失败"))
    })
  }

  onOpened: refreshWorkpieces()

  contentItem: ColumnLayout {
    spacing: 12
    anchors.fill: parent
    anchors.margins: 12

    GroupBox {
      title: qsTr("最新 %1 条工件记录").arg(dataDialog.fetchLimit)
      Layout.fillWidth: true
      Layout.preferredHeight: 260

      ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 6

        RowLayout {
          Layout.fillWidth: true
          Label {
            text: listBusy ? qsTr("加载中…") : qsTr("当前显示：%1").arg(workpieceModel.count)
            color: "#888888"
            Layout.fillWidth: true
          }
          Button {
            text: qsTr("刷新")
            enabled: !listBusy && !dataDialog.busy
            onClicked: refreshWorkpieces()
          }
        }

        ListView {
          id: workpieceList
          Layout.fillWidth: true
          Layout.fillHeight: true
          clip: true
          spacing: 4
          model: workpieceModel
          delegate: Rectangle {
            width: workpieceList.width
            height: 72
            radius: 4
            color: index % 2 === 0 ? "#1a1a1a" : "#121212"
            border.color: "#222222"

            RowLayout {
              anchors.fill: parent
              anchors.margins: 8
              spacing: 8

              ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                Label {
                  text: (code ? code : qsTr("未命名")) + " · " + (type ? type : qsTr("未分类"))
                  font.bold: true
                  color: "#f0f0f0"
                  elide: Text.ElideRight
                }
                Label {
                  text: qsTr("%1 | %2").arg(material || qsTr("材料未设")).arg(dimensions || "-")
                  color: "#cccccc"
                  font.pointSize: 10
                  elide: Text.ElideRight
                }
                Label {
                  text: (surface && surface.length > 0 ? surface : qsTr("表面要求未设")) + " • " + (createdAt || qsTr("未记录时间"))
                  color: "#888888"
                  font.pointSize: 9
                  elide: Text.ElideRight
                }
              }

              ColumnLayout {
                spacing: 4
                Label {
                  text: roughness !== "" ? qsTr("Ra %1").arg(roughness) : qsTr("粗糙度未设")
                  color: "#cccccc"
                }
                Button {
                  text: qsTr("删除")
                  enabled: !dataDialog.busy
                  onClicked: dataDialog.deleteWorkpiece(workpieceId)
                }
              }
            }
          }

          ScrollBar.vertical: ScrollBar { }
        }

        Label {
          visible: !listBusy && workpieceModel.count === 0
          text: qsTr("暂无数据")
          color: "#888888"
          horizontalAlignment: Text.AlignHCenter
          Layout.fillWidth: true
        }
      }
    }

    GroupBox {
      title: qsTr("添加工件")
      Layout.fillWidth: true

      ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8

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
