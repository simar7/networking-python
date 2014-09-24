#!/usr/bin/python
'''
    ECE 358: Computer Networks
    Project: M/D/1 and M/D/1/K Queue Simulation
    Author:  Simarpreet Singh (s244sing@uwaterloo.ca)
             Louisa Chong (l5chong@uwaterloo.ca)
'''
import sys
import random
import math
import threading
import time

INTERVAL = 0.000001
# number of the ticks which the program will be running for
TICKS = 100
# average number of packet generated
LAMBDA = 100
# service time received by a packet
C = 1

def i():
  u = random.random()
  x = (-1/LAMBDA)*math.log(1-u)
  x_tick = x/INTERVAL

def clock(interval):
  threading.Timer(interval, clock, [interval]).start()
  i()
  print "time: {}".format(time.time())

def main():
  global TICKS
  TICKS = int(sys.argv[1])
  global LAMBDA
  LAMBDA= float(sys.argv[2])
  global C
  C = float(sys.argv[3])

if __name__ == '__main__':
    main()
