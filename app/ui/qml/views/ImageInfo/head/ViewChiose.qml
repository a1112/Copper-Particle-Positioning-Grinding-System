import QtQuick
import QtQuick.Controls.Material
import "../../../cores" as Cores
import "../../../components/Base" as Base
Row{
    spacing: 5
    Repeater{
        model: Cores.CoreUI.dataViewModels
        ViewChioseItem{
            text:modelData
        }
    }
}
