import QtQuick 2.15
import QtQuick.Controls 2.15
Item{

FontLoader{
    id:fL
    source:"DS-DIGIT.TTF"
}
Component.onCompleted: {
console.log("加载字体 "+fL.name)
}
}
