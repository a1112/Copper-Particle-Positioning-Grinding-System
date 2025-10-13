pragma Singleton
import QtQuick

Item {

    function get(url, success, failure)
    {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", url);
        xhr.onreadystatechange = function() {
            handleResponse(xhr, success, failure);
        }
        xhr.send();
    }

    // POST
    function post(url, arg, success, failure)
    {

        // WARNING: For POST requests, body is set to null by browsers.
        var data = JSON.stringify(arg);

        var xhr = new XMLHttpRequest();
        xhr.withCredentials = true;
        xhr.onreadystatechange = function() {
            handleResponse(xhr, success, failure);
        }
        xhr.open("POST", url);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(data);
//        // WARNING: For POST requests, body is set to null by browsers.
//        data = JSON.stringify(data)

//        var xhr = new XMLHttpRequest()
//        xhr.withCredentials = true

//        xhr.addEventListener("readystatechange", function() {
//          if(this.readyState === 4) {
//            console.log(this.responseText)
//          }
//        })

//        xhr.open("POST", url,true)
//        xhr.setRequestHeader("Content-Type", "application/json")

//        xhr.send(data)
//        xhr.open("POST", url)
////        xhr.setRequestHeader("Content-Length", arg.length)
////        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;")  //用POST的时候一定要有这句
//        xhr.onreadystatechange = function() {
//            handleResponse(xhr, success, failure)
//        }
//        xhr.send(data)
    }


    // 处理返回值
    function handleResponse(xhr, success, failure){
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status ===  200){
                if (success !== null && success !== undefined)
                {
                    var result = xhr.responseText
                                   success(result)
                }
            }
            else{
                if (failure !== null && failure !== undefined)
                    failure(xhr.responseText, xhr.status)
            }
        }
    }

    Component.onCompleted: {
    }

}
