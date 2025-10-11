import QtQuick
ListView{
    model:5
    orientation: ListView.Horizonta
    interactive: false
    delegate:
        ReOrderItem{
        onReorder: {
            console.log(from,"  ",to)
        }
        dropItem:Rectangle{
            width: 100
            height: 200
            color: "red"
        }
    }
}

