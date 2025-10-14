import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components/btns" as Btns

Dialog {
  id: testDialog
  property var apiClient

  title: "测试图片选择"
  parent: Overlay.overlay
  modal: true
  width: Math.min(920, parent ? parent.width - 80 : 920)
  height: Math.min(600, parent ? parent.height - 80 : 600)
  standardButtons: Dialog.Close

  function openAndRefresh(){ open(); refreshGroups() }

  function refreshGroups(){
    groupsModel.clear(); imagesModel.clear(); selectedSerial=''; selectedImage='';
    if (!apiClient) return;
    apiClient.listGroups(function(resp){
      if (resp && resp.groups) {
        for (var i=0;i<resp.groups.length;i++) {
          var g = resp.groups[i];
          groupsModel.append({ serial: g.serial, note: g.note||'', created_at: g.created_at||'' });
        }
      }
    }, function(s,m){ console.log('list groups err', s, m); })
  }

  function refreshImages(serial){
    imagesModel.clear(); selectedSerial = serial; selectedImage='';
    if (!apiClient || !serial) return;
    apiClient.listGroupImages(serial, function(resp){
      if (resp && resp.files) {
        for (var i=0;i<resp.files.length;i++) {
          imagesModel.append({ name: resp.files[i] });
        }
      }
    }, function(s,m){ console.log('list images err', s, m); })
  }

  property string selectedSerial: ''
  property string selectedImage: ''

  contentItem: Rectangle {
    color: "#1a1a1a"
    anchors.fill: parent
    ColumnLayout {
      anchors.fill: parent
      spacing: 8
      anchors.margins: 8
      RowLayout {
        Layout.fillWidth: true
        Label { text: "测试组"; font.bold: true }
        Btns.ActionButton { text: "刷新"; onClicked: testDialog.refreshGroups() }
        Item { Layout.fillWidth: true }
        TextField { id: tfSerial; placeholderText: "新建组流水号"; width: 200 }
        TextField { id: tfNote; placeholderText: "说明(可选)"; width: 240 }
        Button { text: "创建"; onClicked: {
            if (!tfSerial.text || tfSerial.text.length===0) return;
            apiClient && apiClient.createGroup(tfSerial.text, tfNote.text, function(_){ testDialog.refreshGroups(); }, function(s,m){ console.log('create group err', s, m); })
          } }
      }
      SplitView {
        Layout.fillWidth: true
        Layout.fillHeight: true
        ListView {
          id: lvGroups
          SplitView.preferredWidth: 320
          model: ListModel { id: groupsModel }
          clip: true
          delegate: Rectangle {
            width: lvGroups.width; height: 36; color: (ListView.isCurrentItem? '#2a2a2a':'transparent')
            RowLayout { anchors.fill: parent; anchors.margins: 6
              Label { text: serial; Layout.fillWidth: true }
              Label { text: note; color: '#888' }
            }
            MouseArea { anchors.fill: parent; onClicked: { lvGroups.currentIndex=index; testDialog.refreshImages(serial) } }
          }
        }
        ListView {
          id: lvImages
          SplitView.preferredWidth: 420
          model: ListModel { id: imagesModel }
          clip: true
          delegate: Rectangle {
            width: lvImages.width; height: 32; color: (ListView.isCurrentItem? '#2a2a2a':'transparent')
            RowLayout { anchors.fill: parent; anchors.margins: 6
              Label { text: name; Layout.fillWidth: true }
            }
            MouseArea { anchors.fill: parent; onClicked: { lvImages.currentIndex=index; testDialog.selectedImage=name } }
          }
        }
      }
      RowLayout {
        Layout.fillWidth: true
        Button { text: "加载默认"; onClicked: apiClient && apiClient.loadDefaultImage(function(_){}, function(s,m){}) }
        Button { text: "加载所选"; enabled: (testDialog.selectedSerial && testDialog.selectedImage); onClicked: {
            var rel = testDialog.selectedSerial + '/' + testDialog.selectedImage;
            apiClient && apiClient.loadTestImage(rel, function(_){}, function(s,m){})
          } }
        Item { Layout.fillWidth: true }
        Button { text: "关闭"; onClicked: testDialog.close() }
      }
    }
  }
}
