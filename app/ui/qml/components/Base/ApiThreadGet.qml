import QtQuick
Item{
    id:root
    property alias interval: t_d.interval
    property alias repeat: t_d.repeat
    property alias url: t_d.url
    signal started()
    signal finished(var api_data)
    function start(){
    return t_d.start()
    }
    function quit(){
    return t_d.quit()
    }
    property bool runing: false
    onRuningChanged: {
        if(runing)
        {
            start()
        }
        else{
            quit()
        }
    }
    function restart(){
    return t_d.restart()
    }
    Connections{
        target: t_d
        function onFinish(data){// 执行完成
                finished(data)
        }
    }
    }


