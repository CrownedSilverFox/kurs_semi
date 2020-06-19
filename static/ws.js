function isFunction(functionToCheck) {
    let getType = {};
    return functionToCheck && getType.toString.call(functionToCheck) === '[object Function]';
}

function WS() {
    let self = this;
    let websock;
    this.handlers = {};

    this.connect = function (host, port, uri) {
        websock = new WebSocket("ws://" + host + ":" + port + uri);
        websock.onmessage = function (evt) {
            //TODO: перехватывать и обрабатывать полученные не JSON данные
            let data = JSON.parse(evt.data);
            //log("message received: " + JSON.stringify(data));
            if ((data["key"]) && (isFunction(self.handlers[data["key"]]))) {
                self.handlers[data["key"]](data);
            }

        };

        websock.onclose = function (evt) {
            // console.log("***Подключение разорвано***");
            // connect_form.$port.css("background", "#ff0000");
            // connect_form.$host.css("background", "#ff0000");
            // connect_form.show();
            alert("Отключено");
        };

        websock.onopen = function (evt) {
            //log("***Connection Open***");
            // connect_form.hide();
        };
    };

    this.send = function (obj) {
        websock.send(JSON.stringify(obj));
    };

    this.handleEvents = function (cb, event_type) {
        self.handlers[event_type] = cb;
    };

    // return ws;
}