#!/usr/bin/python
'''
    ECE 358: Computer Networks
    Project: M/D/1 and M/D/1/K Queue Simulation
    Author:  Simarpreet Singh (s244sing@uwaterloo.ca)
             Louisa Chong (l5chong@uwaterloo.ca)
'''

import sys
import time

# TODO: I think this is okay but I'll ask the TA and the prof.
# worst case we will end up writing our own clock.
def tick_tock(tick_duration):
    time.sleep(tick_duration)

def main(argv):
    TOTAL_TICKS = int(argv[1])
    tick_duration = float(argv[2])

    for tick in xrange(0, TOTAL_TICKS):
        print "Sleeping for %s seconds" % tick_duration
        tick_tock(tick_duration)

if __name__ == '__main__':
    main(sys.argv)
