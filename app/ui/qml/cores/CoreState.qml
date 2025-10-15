pragma Singleton
import QtQuick
import QtCore

Item {
  id: root
  // Last selected main view tab
  property int selectedTabIndex: 0
  // Optional: last selected view id
  property string selectedViewId: ""


  property int realViewIndex: 0
  Settings {
    id: st
    category: "CoreState"
    // Persist fields
    property alias selectedTabIndex: root.selectedTabIndex
    property alias selectedViewId: root.selectedViewId
  }
}

