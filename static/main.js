let UE = [];
let uri = '/data/';
let myMap;
let ws;

function User() {
    let self = this;

    this.init = function (data) {
        self.points = [data.position];
        self.id = data.id;
        self.color = generate_color();
        console.log(self.color)
        // console.log(data.position);
    };

    this.add_point = function (data) {
        self.points.push(data.position);
        // console.log(data.position);
    }
}

function handle_points(data) {
    console.log('received:');
    console.log(data);
    for (let user_id of UE.keys()) {
        UE[user_id].add_point(data.users[user_id]);
        let line = new ymaps.AnimatedLine(UE[user_id].points.slice(-2), {}, {
            // Задаем цвет.
            strokeColor: UE[user_id].color,
            // Задаем ширину линии.
            strokeWidth: 5,
            // Задаем длительность анимации.
            animationTime: data.latency - 100
        });
        myMap.geoObjects.add(line);
        line.animate();
    }
}

function generate_color() {
    function getRandomInt(min, max) {
        min = Math.ceil(min);
        max = Math.floor(max);
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    let red = getRandomInt(0, 256);
    let blue = getRandomInt(0, 256);
    let green = getRandomInt(0, 256);
    let red_placeholder = "";
    let green_placeholder = "";
    let blue_placeholder = "";
    if (red < 16) {
        red_placeholder = "0"
    }
    if (green < 16) {
        green_placeholder = "0"
    }
    if (blue < 16) {
        blue_placeholder = "0"
    }
    return red_placeholder + red.toString(16) + green_placeholder + green.toString(16) + blue_placeholder + blue.toString(16) + "80"
}

function handle_init(data) {
    for (let user of data.users) {
        let user_classed = new User();
        user_classed.init(user);
        UE[user.id] = user_classed;
    }
    myMap = new ymaps.Map("map", {
        center: data.center,
        zoom: 16
    }, {
        searchControlProvider: 'yandex#search'
    });

    console.log('connected');
    console.log(UE);
}

function send_configuration() {
    console.log('sending');
    let data = {};
    data['key'] = 'config';
    data['latency'] = $('#latency').val();
    data['points_num'] = $('#points_num').val();
    data['speed'] = $('#speed').val();
    console.log(data);
    ws.send(data);
}

function send_start() {
    $('#start').hide();
    $('#resume').show();
    ws.send({"key": "start"})
}

function send_stop() {
    ws.send({"key": "stop"})
}

function send_resume() {
    ws.send({"key": "resume"})
}

$(function () {
    ws = new WS();

    ymaps.ready(['AnimatedLine']).then(function () {
        console.log('ready');
        ws.connect('localhost', '8888', uri);
    });

    ws.handleEvents(handle_init, "init");
    ws.handleEvents(handle_points, 'points');
});