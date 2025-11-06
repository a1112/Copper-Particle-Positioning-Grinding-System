import QtQuick.Controls
import QtQuick.Layouts
import QtQuick


Page {
  id: page1
  property var data: ({})
  property var formData: defaultTemplate()

  function defaultTemplate() {
    return {
      pre_process: {
        roi: { z_min: 0.0, z_max: 0.0, x_min: 0.0, x_max: 0.0, y_min: 0.0, y_max: 0.0 },
        segmentation: { distance: 0.0, min_points: 0, max_points: 0, diameter_min: 0.0, diameter_max: 0.0 },
        plane_distance: {
          enabled: false,
          sample_distance: 10.0,
          angle_threshold: 1.5,
          distance_threshold: 10.0,
          plane_distance_min: 3.0,
          plane_distance_max: 100.0
        },
        clustering: { distance_threshold: 5.0, min_points: 5000, max_points: 5000000 }
      },
      defect: {
        normal_threshold: 0.0,
        cylinder_offset: { left: 0.0, right: 0.0, up: 0.0, down: 0.0 },
        bulge_thresholds: { center_low: 0.0, center_high: 0.0, edge_low: 0.0, edge_high: 0.0 },
        cylinder_height_threshold: 0.0,
        cylinders: {
          left: { height_origin: 0.0, extend_x: 0.0, extend_y: 0.0 },
          right: { height_origin: 0.0, extend_x: 0.0, extend_y: 0.0 },
          up: { height_origin: 0.0, extend_x: 0.0, extend_y: 0.0 },
          down: { height_origin: 0.0, extend_x: 0.0, extend_y: 0.0 }
        },
        render_range_scale: 0.0,
        connection_distance: 0.0
      },
      path_planning: {
        tool_diameter: 0.0,
        particle_peak_offset: 0.0,
        plate_offset: 0.0,
        z_step_mode: 0,
        z_step_fixed: 0.0,
        z_step_linear_k: 0.0,
        z_step_linear_b: 0.0,
        z_step_min: 0.0,
        z_step_max: 0.0,
        y_step_mode: 0,
        y_step_fixed: 0.0,
        y_step_coeff: 0.0,
        sort_mode: 0,
        cylinder_safe_distance: 0.0,
        lift_height: 0.0,
        cut_start_offset: 0.0,
        end_offset_left: 0.0,
        end_offset_right: 0.0,
        offset: { x: 0.0, y: 0.0, z: 0.0 }
      },
      pose_transform: {
        translation: { x: 0.0, y: 0.0, z: 0.0 },
        rotation: { x: 0.0, y: 0.0, z: 0.0 },
        type: 0
      }
    }
  }

  function deepCopy(obj) { return JSON.parse(JSON.stringify(obj)) }

  function mergeDefaults(source) {
    var base = deepCopy(defaultTemplate())
    function merge(target, incoming) {
      if (!incoming) return
      for (var key in incoming) {
        if (!incoming.hasOwnProperty(key)) continue
        var value = incoming[key]
        if (value !== null && typeof value === "object" && !Array.isArray(value)) {
          if (!(key in target) || typeof target[key] !== "object")
            target[key] = {}
          merge(target[key], value)
        } else {
          target[key] = value
        }
      }
    }
    merge(base, source)
    return base
  }

  onDataChanged: formData = mergeDefaults(data)
  Component.onCompleted: formData = mergeDefaults(data)

  function collectPayload() {
    return deepCopy(formData)
  }

  function getValue(path, fallback) {
    var node = formData
    var parts = path.split('.')
    for (var i = 0; i < parts.length; ++i) {
      var key = parts[i]
      if (!node || !(key in node))
        return fallback
      node = node[key]
    }
    return node !== undefined ? node : fallback
  }

  function setValue(path, value) {
    var parts = path.split('.')
    var node = formData
    for (var i = 0; i < parts.length - 1; ++i) {
      var key = parts[i]
      if (!(key in node) || typeof node[key] !== "object")
        node[key] = {}
      node = node[key]
    }
    node[parts[parts.length - 1]] = value
    formData = deepCopy(formData)
  }

  function setNumeric(path, text) {
    var value = Number(text)
    if (isNaN(value))
      value = 0
    setValue(path, value)
  }

  function setInteger(path, text) {
    var value = parseInt(text, 10)
    if (isNaN(value))
      value = 0
    setValue(path, value)
  }

  function setBoolean(path, checked) {
    setValue(path, !!checked)
  }

  Flickable {
    anchors.fill: parent
    contentWidth: width
    contentHeight:col.height
    clip: true
    flickableDirection: Flickable.VerticalFlick
    ScrollBar.vertical: ScrollBar { }

    ColumnLayout {
      id:col
      width: parent.width
      spacing: 16
      anchors.margins: 12

      Label {
        text: qsTr("算法参数设置")
        font.pixelSize: 18
        font.bold: true
        color: "#f8fafc"
      }

      // Pre-process ROI
      GroupBox {
        title: qsTr("预处理 · 空间 ROI")
        Layout.fillWidth: true
          GridLayout {
            columns: 6
            columnSpacing: 12
            rowSpacing: 8
            Label { text: qsTr("Z 最小 (mm)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.roi.z_min", 0)); onEditingFinished: setNumeric("pre_process.roi.z_min", text) }
            Label { text: qsTr("Z 最大 (mm)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.roi.z_max", 0)); onEditingFinished: setNumeric("pre_process.roi.z_max", text) }
            Label { text: qsTr("X 最小 (mm)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.roi.x_min", 0)); onEditingFinished: setNumeric("pre_process.roi.x_min", text) }
            Label { text: qsTr("X 最大 (mm)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.roi.x_max", 0)); onEditingFinished: setNumeric("pre_process.roi.x_max", text) }
            Label { text: qsTr("Y 最小 (mm)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.roi.y_min", 0)); onEditingFinished: setNumeric("pre_process.roi.y_min", text) }
            Label { text: qsTr("Y 最大 (mm)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.roi.y_max", 0)); onEditingFinished: setNumeric("pre_process.roi.y_max", text) }
          }

      }

      // Pre-process segmentation
      GroupBox {
        title: qsTr("预处理 · 初步分割")
        Layout.fillWidth: true
          GridLayout {
            columns: 6
            columnSpacing: 12
            rowSpacing: 8
            Label { text: qsTr("领域距离 (mm)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.segmentation.distance", 0)); onEditingFinished: setNumeric("pre_process.segmentation.distance", text) }
            Label { text: qsTr("最小点数"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.segmentation.min_points", 0)); inputMethodHints: Qt.ImhDigitsOnly; onEditingFinished: setInteger("pre_process.segmentation.min_points", text) }
            Label { text: qsTr("最大点数"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.segmentation.max_points", 0)); inputMethodHints: Qt.ImhDigitsOnly; onEditingFinished: setInteger("pre_process.segmentation.max_points", text) }
            Label { text: qsTr("直径最小 (mm)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.segmentation.diameter_min", 0)); onEditingFinished: setNumeric("pre_process.segmentation.diameter_min", text) }
            Label { text: qsTr("直径最大 (mm)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.segmentation.diameter_max", 0)); onEditingFinished: setNumeric("pre_process.segmentation.diameter_max", text) }
          }
      }

      // Plane distance
      GroupBox {
        title: qsTr("预处理 · 平面距离筛选")
        Layout.fillWidth: true
        ColumnLayout {
          anchors.fill: parent
          anchors.margins: 12
          RowLayout {
            spacing: 12
            Switch {
              checked: getValue("pre_process.plane_distance.enabled", false)
              onToggled: setBoolean("pre_process.plane_distance.enabled", checked)
            }
            Label { text: qsTr("启用平面距离约束"); color: "#e2e8f0" }
          }
          GridLayout {
            columns: 2
            columnSpacing: 12
            rowSpacing: 8
            Label { text: qsTr("采样距离 (mm)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.plane_distance.sample_distance", 10)); onEditingFinished: setNumeric("pre_process.plane_distance.sample_distance", text) }
            Label { text: qsTr("角度阈值"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.plane_distance.angle_threshold", 1.5)); onEditingFinished: setNumeric("pre_process.plane_distance.angle_threshold", text) }
            Label { text: qsTr("距离阈值"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.plane_distance.distance_threshold", 10)); onEditingFinished: setNumeric("pre_process.plane_distance.distance_threshold", text) }
            Label { text: qsTr("到平面距离最小"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.plane_distance.plane_distance_min", 3)); onEditingFinished: setNumeric("pre_process.plane_distance.plane_distance_min", text) }
            Label { text: qsTr("到平面距离最大"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.plane_distance.plane_distance_max", 100)); onEditingFinished: setNumeric("pre_process.plane_distance.plane_distance_max", text) }
          }
        }
      }

      // Clustering
      GroupBox {
        title: qsTr("预处理 · 聚类")
        Layout.fillWidth: true
        ColumnLayout {
          anchors.fill: parent
          anchors.margins: 12
          GridLayout {
            columns: 2
            columnSpacing: 12
            rowSpacing: 8
            Label { text: qsTr("聚类距离阈值"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.clustering.distance_threshold", 5)); onEditingFinished: setNumeric("pre_process.clustering.distance_threshold", text) }
            Label { text: qsTr("最小点数"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.clustering.min_points", 5000)); inputMethodHints: Qt.ImhDigitsOnly; onEditingFinished: setInteger("pre_process.clustering.min_points", text) }
            Label { text: qsTr("最大点数"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pre_process.clustering.max_points", 5000000)); inputMethodHints: Qt.ImhDigitsOnly; onEditingFinished: setInteger("pre_process.clustering.max_points", text) }
          }
        }
      }

      // Defect parameters
      GroupBox {
        title: qsTr("缺陷提取参数")
        Layout.fillWidth: true
        ColumnLayout {
          anchors.fill: parent
          anchors.margins: 12
          GridLayout {
            columns: 2
            columnSpacing: 12
            rowSpacing: 8
            Label { text: qsTr("法线阈值"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("defect.normal_threshold", 0)); onEditingFinished: setNumeric("defect.normal_threshold", text) }
            Label { text: qsTr("左侧偏移"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("defect.cylinder_offset.left", 0)); onEditingFinished: setNumeric("defect.cylinder_offset.left", text) }
            Label { text: qsTr("右侧偏移"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("defect.cylinder_offset.right", 0)); onEditingFinished: setNumeric("defect.cylinder_offset.right", text) }
            Label { text: qsTr("上侧偏移"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("defect.cylinder_offset.up", 0)); onEditingFinished: setNumeric("defect.cylinder_offset.up", text) }
            Label { text: qsTr("下侧偏移"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("defect.cylinder_offset.down", 0)); onEditingFinished: setNumeric("defect.cylinder_offset.down", text) }
            Label { text: qsTr("中心阈值下限"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("defect.bulge_thresholds.center_low", 0)); onEditingFinished: setNumeric("defect.bulge_thresholds.center_low", text) }
            Label { text: qsTr("中心阈值上限"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("defect.bulge_thresholds.center_high", 0)); onEditingFinished: setNumeric("defect.bulge_thresholds.center_high", text) }
            Label { text: qsTr("边缘阈值下限"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("defect.bulge_thresholds.edge_low", 0)); onEditingFinished: setNumeric("defect.bulge_thresholds.edge_low", text) }
            Label { text: qsTr("边缘阈值上限"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("defect.bulge_thresholds.edge_high", 0)); onEditingFinished: setNumeric("defect.bulge_thresholds.edge_high", text) }
            Label { text: qsTr("气缸高度偏差阈值"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("defect.cylinder_height_threshold", 0)); onEditingFinished: setNumeric("defect.cylinder_height_threshold", text) }
            Label { text: qsTr("高度渲染系数"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("defect.render_range_scale", 0)); onEditingFinished: setNumeric("defect.render_range_scale", text) }
            Label { text: qsTr("聚类距离 (mm)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("defect.connection_distance", 0)); onEditingFinished: setNumeric("defect.connection_distance", text) }
          }

          Label { text: qsTr("四向气缸区域"); color: "#e2e8f0"; Layout.topMargin: 12 }
          GridLayout {
            columns: 4
            columnSpacing: 10
            rowSpacing: 6
            Repeater {
              model: [
                { key: "left", label: qsTr("左气缸") },
                { key: "right", label: qsTr("右气缸") },
                { key: "up", label: qsTr("上气缸") },
                { key: "down", label: qsTr("下气缸") }
              ]
              delegate: ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                Label { text: modelData.label; color: "#cbd5f5" }
                RowLayout {
                  spacing: 6
                  Label { text: qsTr("高度"); color: "#9aa0b5" }
                  TextFieldBase {
                    text: String(getValue("defect.cylinders." + modelData.key + ".height_origin", 0))
                    Layout.preferredWidth: 80
                    onEditingFinished: setNumeric("defect.cylinders." + modelData.key + ".height_origin", text)
                  }
                  Label { text: "X"; color: "#9aa0b5" }
                  TextFieldBase {
                    text: String(getValue("defect.cylinders." + modelData.key + ".extend_x", 0))
                    Layout.preferredWidth: 60
                    onEditingFinished: setNumeric("defect.cylinders." + modelData.key + ".extend_x", text)
                  }
                  Label { text: "Y"; color: "#9aa0b5" }
                  TextFieldBase {
                    text: String(getValue("defect.cylinders." + modelData.key + ".extend_y", 0))
                    Layout.preferredWidth: 60
                    onEditingFinished: setNumeric("defect.cylinders." + modelData.key + ".extend_y", text)
                  }
                }
              }
            }
          }
        }
      }

      // Path planning
      GroupBox {
        title: qsTr("加工路径规划")
        Layout.fillWidth: true
        ColumnLayout {
          anchors.fill: parent
          anchors.margins: 12
          GridLayout {
            columns: 2
            columnSpacing: 12
            rowSpacing: 8
            Label { text: qsTr("刀具直径 (mm)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.tool_diameter", 0)); onEditingFinished: setNumeric("path_planning.tool_diameter", text) }
            Label { text: qsTr("粒子最高点上抬"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.particle_peak_offset", 0)); onEditingFinished: setNumeric("path_planning.particle_peak_offset", text) }
            Label { text: qsTr("铜板上抬距离"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.plate_offset", 0)); onEditingFinished: setNumeric("path_planning.plate_offset", text) }
            Label { text: qsTr("Z 进给模式"); color: "#e2e8f0" }
            ComboBox {
              model: [qsTr("固定进给"), qsTr("线性进给")]
              currentIndex: Number(getValue("path_planning.z_step_mode", 0))
              onActivated: setInteger("path_planning.z_step_mode", index)
            }
            Label { text: qsTr("固定 Z 进给"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.z_step_fixed", 0)); onEditingFinished: setNumeric("path_planning.z_step_fixed", text) }
            Label { text: qsTr("Z 进给系数 K"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.z_step_linear_k", 0)); onEditingFinished: setNumeric("path_planning.z_step_linear_k", text) }
            Label { text: qsTr("Z 进给截距 B"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.z_step_linear_b", 0)); onEditingFinished: setNumeric("path_planning.z_step_linear_b", text) }
            Label { text: qsTr("Z 进给最小"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.z_step_min", 0)); onEditingFinished: setNumeric("path_planning.z_step_min", text) }
            Label { text: qsTr("Z 进给最大"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.z_step_max", 0)); onEditingFinished: setNumeric("path_planning.z_step_max", text) }
            Label { text: qsTr("Y 进给模式"); color: "#e2e8f0" }
            ComboBox {
              model: [qsTr("固定进给"), qsTr("刀盘系数")]
              currentIndex: Number(getValue("path_planning.y_step_mode", 0))
              onActivated: setInteger("path_planning.y_step_mode", index)
            }
            Label { text: qsTr("固定 Y 进给距"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.y_step_fixed", 0)); onEditingFinished: setNumeric("path_planning.y_step_fixed", text) }
            Label { text: qsTr("Y 进给系数"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.y_step_coeff", 0)); onEditingFinished: setNumeric("path_planning.y_step_coeff", text) }
            Label { text: qsTr("加工排序"); color: "#e2e8f0" }
            ComboBox {
              model: [qsTr("从上到下"), qsTr("从左到右")]
              currentIndex: Number(getValue("path_planning.sort_mode", 0))
              onActivated: setInteger("path_planning.sort_mode", index)
            }
            Label { text: qsTr("气缸安全距离"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.cylinder_safe_distance", 0)); onEditingFinished: setNumeric("path_planning.cylinder_safe_distance", text) }
            Label { text: qsTr("抬刀高度"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.lift_height", 0)); onEditingFinished: setNumeric("path_planning.lift_height", text) }
            Label { text: qsTr("下刀位置偏移"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.cut_start_offset", 0)); onEditingFinished: setNumeric("path_planning.cut_start_offset", text) }
            Label { text: qsTr("路径左偏移"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.end_offset_left", 0)); onEditingFinished: setNumeric("path_planning.end_offset_left", text) }
            Label { text: qsTr("路径右偏移"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.end_offset_right", 0)); onEditingFinished: setNumeric("path_planning.end_offset_right", text) }
            Label { text: qsTr("整体偏移 X"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.offset.x", 0)); onEditingFinished: setNumeric("path_planning.offset.x", text) }
            Label { text: qsTr("整体偏移 Y"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.offset.y", 0)); onEditingFinished: setNumeric("path_planning.offset.y", text) }
            Label { text: qsTr("整体偏移 Z"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("path_planning.offset.z", 0)); onEditingFinished: setNumeric("path_planning.offset.z", text) }
          }
        }
      }

      // Pose transform
      GroupBox {
        title: qsTr("标定姿态")
        Layout.fillWidth: true
        ColumnLayout {
          anchors.fill: parent
          anchors.margins: 12
          GridLayout {
            columns: 2
            columnSpacing: 12
            rowSpacing: 8
            Label { text: qsTr("平移 X (mm)"); color: "#e2e8f0" }
            TextFieldBase{ text: String(getValue("pose_transform.translation.x", 0)); onEditingFinished: setNumeric("pose_transform.translation.x", text) }
            Label { text: qsTr("平移 Y (mm)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pose_transform.translation.y", 0)); onEditingFinished: setNumeric("pose_transform.translation.y", text) }
            Label { text: qsTr("平移 Z (mm)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pose_transform.translation.z", 0)); onEditingFinished: setNumeric("pose_transform.translation.z", text) }
            Label { text: qsTr("旋转 X (°)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pose_transform.rotation.x", 0)); onEditingFinished: setNumeric("pose_transform.rotation.x", text) }
            Label { text: qsTr("旋转 Y (°)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pose_transform.rotation.y", 0)); onEditingFinished: setNumeric("pose_transform.rotation.y", text) }
            Label { text: qsTr("旋转 Z (°)"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pose_transform.rotation.z", 0)); onEditingFinished: setNumeric("pose_transform.rotation.z", text) }
            Label { text: qsTr("Pose 类型"); color: "#e2e8f0" }
            TextFieldBase { text: String(getValue("pose_transform.type", 0)); inputMethodHints: Qt.ImhDigitsOnly; onEditingFinished: setInteger("pose_transform.type", text) }
          }
        }
      }

      Item { Layout.fillHeight: true }
    }
  }
}
