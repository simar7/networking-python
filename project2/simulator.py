#!/usr/bin/python
'''
    ECE 358: Computer Networks
    Project: CSMA/CD protocols
    Author:  Simarpreet Singh (s244sing@uwaterloo.ca)
             Louisa Chong (l5chong@uwaterloo.ca)

'''
import sys
import argparse
import logging
import math


SERVERS        = 0
ARRIVAL_RATE   = 0
LAN_SPEED      = 0
PACKET_LEN     = 0
P_PARM         = "1"
ETHERNET_SPEED = 2e10     # propagation speed of ethernet
TICK_DURATION  = 0
D_TRANS        = 0
D_TOTAL_PROP   = 0

class Packet:
    sender = None
    sender_index = -1
    send_time = -2
    def __init__(self, sender, sender_index, send_time):
        self.sender = sender
        self.sender_index = sender_index
        self.send_time = send_time

    def is_detected(self, from_index, current_tick):
        """ Check if the the packet can be sensed from the given index
        Keyword arguments:
        @from_index: index where the are sending from
        @current_tick: current time of the simulation (in ticks)
        """
        # how much time have passed
        time_passed = current_tick - self.send_time
        # how far did the signal propagate to on the smaller index side
        min_index = self.sender_index - time_passed
        # how far did the signal propagate to on the larger index side
        max_index = self.sender_index + time_passed
        # determin if the packet is detected
        if (((max_index >= from_index) and (from_index > self.sender_index))
         or ((min_index <= from_index) and (from_index <= self.sender_index))):
            return True
        return False

def main(argv):
    print "Program is starting..."
    test_packet()

def init():
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    parser = argparse.ArgumentParser(description= \
            "CSMA/CA protocols")

    # number of computers
    parser.add_argument('-N', action="store", type=int, default="5")
    # average arrival rate packets per second
    parser.add_argument('-A', action="store", type=float, default="100")
    # speed of Lan in bits per second (default = 1Mbps)
    parser.add_argument('-W', action="store", type=int, default="1000000")
    # packet length in bits (default = 1500bytes
    parser.add_argument('-L', action="store", type=int, default="6000")
    # persistence parameter
    parser.add_argument('-P', action="store", type=str, default="1")
    # the tick intervals
    parser.add_argument('--tickLen', action="store", type=float, default="1.0")

    # args is a type dict.
    argsDict = vars(parser.parse_args())

    global SERVERS
    SERVERS = argsDict['N']
    global ARRIVAL_RATE
    ARRIVAL_RATE = argsDict['A']
    global LAN_SPEED
    LAN_SPEED = argsDict['W']
    global PACKET_LEN
    PACKET_LEN = argsDict['L']
    global P_PARM
    P_PARM = argsDict['P']
    # fixed value for the program
    global TICK_DURATION
    TICK_DURATION = argsDict['tickLen']
    # the total ticks it take for a full packet to be transmitted
    global D_TRANS
    D_TRANS = math.ceil(PACKET_LEN*ARRIVAL_RATE / TICK_DURATION)
    # the total ticks it take for a packet to be propagated
    # from the first node to the last node
    global D_TOTAL_PROP
    D_TOTAL_PROP = math.ceil((10*(SERVERS-1)) / (ETHERNET_SPEED*TICK_DURATION))

    # Let it rip.
    main(argsDict)

if __name__ == '__main__':
    init()
