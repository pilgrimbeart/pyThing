#! /usr/bin/python
'''
Created on 25 Jan 2013

@author: pilgrim
'''
import unittest

class Thing():
    def __init__(self):
        # self.x = ...
        pass

def instantiateThings(n):
    return [Thing() for _ in range(n)]

TEST_NUM_THINGS = 100
    
class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testBasic(self):
        set = instantiateThings(TEST_NUM_THINGS)
        print set

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()