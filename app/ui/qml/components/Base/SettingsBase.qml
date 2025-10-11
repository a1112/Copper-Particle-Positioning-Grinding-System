/*
保持状态信息
*/
import Qt.labs.settings
//  保存本地数据的基本类
Settings{
    fileName:rootConfig.settingFile//"State.ini" //Qt.resolvedUrl("../config/status.ini")
    category:"Base"
}

