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
    parser.add_argument('-P', action="store", type=float, default="1")

    # args is a type dict.
    argsDict = vars(parser.parse_args())

    servers      = argsDict['N']
    arrival_rate = argsDict['A']
    lan_speed    = argsDict['W']
    packet_len   = argsDict['L']
    p_parm       = argsDict['P']

    # Let it rip.
    main(argsDict)

if __name__ == '__main__':
    init()
