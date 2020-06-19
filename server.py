import tornado.ioloop
import tornado.web
import tornado.websocket
import json
from random import randint
import socket
from config import *
from math import sin, cos, pi


class IndexHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        return self.render('templates/base.html')

    def get_template_namespace(self):
        namespace = dict(
            handler=self,
            request=self.request,
            current_user=self.current_user,
            locale=self.locale,
            _=self.locale.translate,
            pgettext=self.locale.pgettext,
            static_url=self.static_url,
            xsrf_form_html=self.xsrf_form_html,
            reverse_url=self.reverse_url,
            default_config={
                'points_num': points_num,
                'latency': latency,
                'speed': speed,
            }
        )
        namespace.update(self.ui)
        return namespace


class Run:
    def __init__(self):
        self.points_num = points_num
        self.points = {}
        self.client = None
        self.latency = latency
        self.periodic = None
        self.speed = speed

        self.message_types = {
            'config': self.set_config,
            'start': self.start,
            'stop': self.stop,
            'resume': self.resume
        }

    def init(self):
        self.points = {}
        self.periodic = tornado.ioloop.PeriodicCallback(self.do_tick, self.latency)

        for i in range(self.points_num):
            x, y = self.generate_movement()
            self.points[i] = (start_point[0] + x,
                              start_point[1] + y)

    def on_connect(self, client):
        self.client = client
        self.init()

    def generate_movement(self):
        degrees = randint(0, 360)
        y = sin(degrees*pi/180)
        x = cos(degrees*pi/180)
        y = (y * self.speed / 360) / 111
        x = (x * self.speed / 360) / 111
        return x, y

    def send_points(self, method):
        self.send_message(
            {'key': method, 'users': [{'id': key, 'position': self.points[key]} for key in self.points.keys()],
             'center': start_point, 'latency': self.latency})

    def calculate(self, user_coords):


    def do_tick(self):
        for key in self.points.keys():
            x, y = self.generate_movement()
            self.points[key] = (
                self.points[key][0] + x,
                self.points[key][1] + y)
            pl, sr = self.calculate(self.points[key])
        self.send_points('points')

    def on_disconnect(self):
        self.periodic.stop()
        self.__init__()

    def message_received(self, message):
        self.message_types[message['key']](message)

    def set_config(self, message):
        def validate(config):
            log_message = []
            valid = True

            if config['latency'] < 500:
                valid = False
                log_message.append('Latency is too low')
            elif config['latency'] > 5000:
                valid = False
                log_message.append('Latency is too big')

            if config['points_num'] <= 0:
                valid = False
                log_message.append('Points count is too low')
            elif config['points_num'] > 10:
                valid = False
                log_message.append('Points count is too big')

            return {'valid': valid, 'log_message': '\n'.join(log_message)}

        for key in message.keys():
            if key == 'key':
                continue
            message[key] = int(message[key])
        validation_result = validate(message)
        if not validation_result['valid']:
            self.send_message({'key': 'invalid_config', 'log': validation_result['log_message']})

        self.latency = message['latency']
        self.points_num = message['points_num']
        self.speed = message['speed']
        self.init()

    def start(self, message):
        self.send_points('init')
        self.periodic.start()

    def resume(self, message):
        self.periodic.start()

    def stop(self, message):
        self.periodic.stop()

    def send_message(self, message):
        self.client.write_message(message)


class WSH(tornado.websocket.WebSocketHandler):
    def open(self):
        self.application.run.on_connect(self)
        print("Connected")

    def on_message(self, message):
        message = json.loads(message)
        application.run.message_received(message)
        print("WSHandler Received message: {}".format(message))

    def on_close(self):
        print("close connection", self)
        self.close()
        self.application.run.on_disconnect()


class Application(tornado.web.Application):
    def __init__(self):
        self.run = Run()

        handlers = [
            (r"/", IndexHandler),
            (r"/data/", WSH),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': "static"}),
        ]

        tornado.web.Application.__init__(self, handlers)


if __name__ == "__main__":
    application = Application()
    sock = 8888
    application.listen(sock)
    myIP = socket.gethostbyname(socket.gethostname())
    print('*** WebSocket Server Started at %s:%s***' % (myIP, sock))
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print('*** Stopped server ***')
        tornado.ioloop.IOLoop.current().stop()
