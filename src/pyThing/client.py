#! /usr/bin/python

from socketIO_client import SocketIO, BaseNamespace
import socket, os
import sys
import cProfile

#HOST = '95.138.176.230' # Pilgrim's Rackspace VM "Rack1"
HOST = 'localhost'
PORT = 3000

g_socketIO = None

def set_object(id,x,y):
# Update object, locally and remotely
    # Update locally
    g_socketIO.emit("foo",{"bar":[1,2,3]})	# Update remote copy


class Namespace(BaseNamespace):

    def on_connect(self, socketIO):
        print '[Connected]'

    def on_disconnect(self):
        print '[Disconnected]'

    def on_error(self, name, message):
        print '[Error] %s: %s' % (name, message)

    def on_(self, eventName, *eventArguments):
        print '[Event] %s: %s' % (eventName, eventArguments)

    def on_message(self, id, message):
        print '[Message] %s: %s' % (id, message)

def main():
    global g_socketIO

    print "Listening to "+HOST+":"+str(PORT)

    g_socketIO = SocketIO(HOST, PORT, Namespace)

    print "Emitting adduser"
    g_socketIO.emit("adduser",socket.getfqdn()+";"+str(os.getpid()))

    g_start_time = time.time()
    if(len(sys.argv)<2):
        print "Usage:",sys.argv[0]," S or L or SL"
    if("S" in sys.argv[1]):
        print "Starting speaking"
        thread1 = threading.Thread(target=heartbeat_thread)
        thread1.start()
    if("L" in sys.argv[1]):
        print "Starting listening"
        g_socketIO.wait()
    else:
        time.sleep(60*60*24*365*100)

if __name__ == "__main__":
    main()
