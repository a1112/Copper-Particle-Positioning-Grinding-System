import QtQuick
import QtQuick.Controls.Material
import "../../../cores" as Cores
Row{

    Repeater{
        model: Cores.CoreUI.dataViewModels
        ViewChioseItem{
            text:modelData
        }
    }
}
