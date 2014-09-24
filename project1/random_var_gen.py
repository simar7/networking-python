#!/usr/bin/python
'''
    ECE 358: Computer Networks
    Project: M/D/1 and M/D/1/K Queue Simulation
    Author:  Simarpreet Singh (s244sing@uwaterloo.ca)
             Louisa Chong (l5chong@uwaterloo.ca)
'''
import sys
import random
import threading
import time

def i():
  u = random.random()
  #TODO: generate packet
  print "u: {}".format(u)
  x = 0
  #TODO: some inverse transform
  print "x: {}".format(x)

def tick(interval):
  threading.Timer(interval, tick, [interval]).start()
  i()
  print "time: {}".format(time.time())

def main():
  tick(float(sys.argv[1]))


if __name__ == '__main__':
    main()
