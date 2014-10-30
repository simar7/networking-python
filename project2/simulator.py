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


SERVERS = 0
ARRIVAL_RATE = 0
LAN_SPEED = 0
PACKET_LEN = 0
P_PARM = "1"


def main(argv):
    print "Program is starting..."

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

    # args is a type dict.
    argsDict = vars(parser.parse_args())

    global SERVERS
    SERVERS      = argsDict['N']
    global ARRIVAL_RATE
    ARRIVAL_RATE = argsDict['A']
    global LAN_SPEED
    LAN_SPEED    = argsDict['W']
    global PACKET_LEN
    PACKET_LEN   = argsDict['L']
    global P_PARM
    P_PARM       = argsDict['P']

    # Let it rip.
    main(argsDict)

if __name__ == '__main__':
    init()
