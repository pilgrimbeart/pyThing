#! /usr/bin/python
'''
Created on 25 Jan 2013

@author: pilgrim

Relative times are in seconds.
Absolute times are in epoch seconds

'''
import unittest
from threading import Timer
import time
from apscheduler.scheduler import Scheduler # Seems so efficient that all callbacks scheduled for the same time seem to happen in one atomic moment
import pprint

TEST_NUM_THINGS = 10000
TEST_RUN_SECS = 1

class ThingStats():
    """A container for generic statistics about Thing objects."""
    def __init__(self):
        self.stats = {}
        self.stats["bornTime"] = None
        self.stats["mostRecentMessageTime"] = None
        self.stats["mostRecentTickTime"] = None
    def set(self,attr,value):
        self.stats[attr]=value
        

class Thing():
    """Base class for an IoT Thing. Supports core semantics, exhibits generic behaviour.
    Care-and-feeding function names start with _""" 
    MESSAGE_START = 1
    
    def __init__(self):
        self.handleMessage = {Thing.MESSAGE_START : Thing.messageStart}
        self._stats = ThingStats()
        self._stats.set("bornTime", time.time())
    
    def _tick(self):
        # print "Thing",self,"ticked"
        self._stats.set("mostRecentTickTime", time.time())
        pass
        
    def receiveMessage(self, msgid):
        self._stats.set("mostRecentMessageTime",time.time())
        self.handleMessage[msgid](self)
        pass

    def messageStart(self):
        # print "Thing",self,"received Message:start"
        pass

def instantiateThings(n):
    return [Thing() for _ in range(n)]

class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testBasic(self):
        class ping():
            def __init__(self):
                self.callbacks = []
            def ping(self):
                for c in self.callbacks:
                    c()
            def addCallback(self, fn):
                self.callbacks.append(fn)

        print "Test running with",TEST_NUM_THINGS,"things for",TEST_RUN_SECS,"secs"
        # Start world
        sched = Scheduler()
        sched.start()
        pinger = ping()
        sched.add_interval_job(pinger.ping, seconds=1)

        print "Instantiating things"
        # Instantiate things
        things = instantiateThings(TEST_NUM_THINGS)
        for t in things:
            pinger.addCallback(t._tick)
        for t in things:
            t.receiveMessage(Thing.MESSAGE_START)

        print "Waiting",TEST_RUN_SECS,"secs"
        time.sleep(TEST_RUN_SECS)   # Let the world run

        print "Done"
        # Stop world
        sched.shutdown(wait=True)   # Gracefully stop

        # Report stats
        
        validstat = ThingStats()
        for s in validstat.stats.keys():
            validstat.stats[s] = 0
            for t in things:
                if t._stats.stats[s] != None:
                    validstat.stats[s] += 1
        
        minstat = ThingStats()
        maxstat = ThingStats()
        for s in minstat.stats.keys():
            for t in things:
            # Check each statistic against each Thing
                if(minstat.stats[s]==None or t._stats.stats[s]<minstat.stats[s]):
                    minstat.stats[s]=t._stats.stats[s]
                if(maxstat.stats[s]==None or t._stats.stats[s]>maxstat.stats[s]):
                    maxstat.stats[s]=t._stats.stats[s]

        rangestat = ThingStats()        
        for s in rangestat.stats.keys():
            if maxstat.stats[s] != None and minstat.stats[s] != None:
                rangestat.stats[s] = maxstat.stats[s] - minstat.stats[s]

        print "Overall Stats:"
        pp = pprint.PrettyPrinter(indent=4, depth=6)
        print "Number of valid stats:",
        pp.pprint(validstat.stats)
        print "Min:",
        pp.pprint(minstat.stats)
        print "Max:",
        pp.pprint(maxstat.stats)
        print "Range:",
        pp.pprint(rangestat.stats)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()