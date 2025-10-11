import QtQuick
Item {

    enum Enum_ViewModel{
    SearchModel=0,  // 查询模式
    DefectModel=1,  // 缺陷模式 路径模式
    CimgModel=2  ,   // 图像模式 路径模式
    RealTimeDefectModel=3, // 实时缺陷模式
    RealTimeSteelModel=4  //  钢板 实时模式
        /*
        图像模式以 seqNo 为基础
    */
    }
    enum PlayModel{//查看模式
    BaseModel=0,    // 人工查看模式
    AutoModel=1,    // 新钢板模式
    RealTimeModel=2 // 自动阅读模式
    }
    enum MainViewModel{
    BaseModel=0,
    SelectDefectModel=1,
    ZoomInModel=2,
    ItemMoveModel=3,
    ClassiflyModel=4
    }
    enum AppViewModel{//窗口模式
        BaseModel=0
    }

    enum JoinModel{//图像的拼接模式
        UserModel=0,
        AutoModel=1
    }
}

