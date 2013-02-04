#! /usr/bin/python

from socketIO_client import SocketIO, BaseNamespace
import socket, os
import sys,time
import threading

HEARTBEAT_SECS = (1.0 / 1.0)

#HOST = '95.138.176.230' # Pilgrim's Rackspace VM "Rack1"
HOST = 'localhost'
PORT = 4000

g_socketIO = None
g_updates = 0
g_start_time = 0

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


def heartbeat():
    g_socketIO.emit("update",{"foobar":[1,2,3]})

def heartbeat_thread():
    # Running at a defined QPS speed is complicated by the facts that:
    # 1) Doing the heartbeat takes time (which we need to subtract from any time we wait)
    # 2) sleep() may not delay at all if passed very small numbers
    # So we use an absolute measure of time, instead of a relative one
    # This does mean that if for some reason we get stalled, we will burst to catch up
    global g_updates, g_start_time
    while(1):
        heartbeat()
        elapsed = time.time() - g_start_time
        timetosleep = max(0, (g_updates+1)*HEARTBEAT_SECS - elapsed)
        g_updates += 1
        print g_updates,"updates,",int(elapsed),"secs (",int(g_updates/elapsed),"/sec) timetosleep=",timetosleep
        time.sleep(timetosleep)


def main():
    global g_socketIO
    global g_start_time

    myname = socket.getfqdn()+";"+str(os.getpid())  # Name = Machine+PID
    print "Client",myname,"starting"
    print "Connecting to"+HOST+":"+str(PORT)

    g_socketIO = SocketIO(HOST, PORT, Namespace)

    print "Emitting adduser",myname
    g_socketIO.emit("adduser", myname)

    g_start_time = time.time()
    
    print "Starting heartbeat"
    thread1 = threading.Thread(target=heartbeat_thread)
    thread1.daemon = True   # So that ^C kills everything
    thread1.start()

    print "About to socketIO.wait()"
    g_socketIO.wait()

if __name__ == "__main__":
    main()
