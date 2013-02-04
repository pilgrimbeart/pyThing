#! /usr/bin/python
# First:
# sudo apt-get install python2.7-dev
# sudo apt-get install libevent-dev
# pip install gevent-socketio

# The most basic-possible Socket.IO server, built for speed testing

from gevent import monkey; monkey.patch_all()

from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin

PORT = 4000

class ChatNamespace(BaseNamespace, BroadcastMixin):

    def on_adduser(self, nickname):
        print "on_adduser",nickname
        self.request['nicknames'].append(nickname)  # TODO: Check this is unique!
        self.socket.session['nickname'] = nickname
        self.broadcast_event_not_me('announce', nickname)           # Tell all (other) clients the delta
        self.broadcast_event('userlist', self.request['nicknames']) # Tell all clients the absolute
        
    def recv_disconnect(self):
        # Remove nickname from the list.
        nickname = self.socket.session['nickname']
        self.request['nicknames'].remove(nickname)
        self.broadcast_event_not_me('unannounce', nickname)
        self.broadcast_event('userlist', self.request['nicknames'])

        self.disconnect(silent=True)

    def on_update(self, msg):
        print "on_update",self.socket.session['nickname'],msg
        self.broadcast_event_not_me('update', msg)

    def recv_message(self, message):
        print "PING!!!", message

class Application(object):
    def __init__(self):
        self.buffer = []
        # Dummy request object to maintain state between Namespace initialization.
        self.request = {
            'nicknames': [],
        }

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'].strip('/')

        if not path:
            start_response('200 OK', [('Content-Type', 'text/html')])
            return ['<h1>Sorry, machines only</h1>']

#        if path.startswith('static/') or path == 'chat.html':
#            try:
#                data = open(path).read()
#            except Exception:
#                return not_found(start_response)
#
#            if path.endswith(".js"):
#                content_type = "text/javascript"
#            elif path.endswith(".css"):
#                content_type = "text/css"
#            elif path.endswith(".swf"):
#                content_type = "application/x-shockwave-flash"
#            else:
#                content_type = "text/html"
#
#            start_response('200 OK', [('Content-Type', content_type)])
#            return [data]

        if path.startswith("socket.io"):
            socketio_manage(environ, {'': ChatNamespace}, self.request)
        else:
            return not_found(start_response)


def not_found(start_response):
    start_response('404 Not Found', [])
    return ['<h1>Not Found</h1>']


if __name__ == '__main__':
    print "Socket.IO server listening on port",PORT," (and on port 843, flash policy server)"
    SocketIOServer(('0.0.0.0', PORT), Application(),
        resource="socket.io", policy_server=True,
        policy_listener=('0.0.0.0', 10843)).serve_forever()