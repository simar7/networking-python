#!/usr/bin/python
'''
    ECE 358: Computer Networks
    Project: M/D/1 and M/D/1/K Queue Simulation
    Author:  Simarpreet Singh (s244sing@uwaterloo.ca)
             Louisa Chong (l5chong@uwaterloo.ca)

Params: [Arrival Process Type] [Service Process Type] [# of Servers] [Buf Size]
Types:
    M: Markovian.
    D: Deterministic.
    G: General
Arrival Process Type (M, D, G):
    Model for the queue.
Service Process Type (M, D, G):
    Model for the receiver.
# of Servers:
    Number of server processes.
Buf Size (limited, infinite):
    Size of the buffer.
'''
import sys
import time
import array
import random
import argparse
import multiprocessing

# TODO: I think this is okay but I'll ask the TA and the prof.
# worst case we will end up writing our own clock.
def tickTock(tickDuration, TOTAL_TICKS):
    for tick in xrange(0, int(TOTAL_TICKS)):
        print "[%s]: Sleeping for %s seconds." % (tickTock.__name__, tickDuration)
        time.sleep(float(tickDuration))

def genData():
    packetData = random.random()
    print "[%s]: Data Generated: %s" % (genData.__name__, packetData)

def transmitter(packetTxData):
    if packetTxData == "None":
        print "[%s]: Nothing to transmit." % (transmitter.__name__)
    else:
        print "[%s]: Sending %s across..." % (transmitter.__name__, packetTxData)

def receiver(packetRxData):
    if packetRxData == "None":
        print "[%s]: Nothing was received." % (receiver.__name__)
    else:
        print "[%s]: Received %s" % (receiver.__name__, packetRxData)

def main(argv):
    print "Program is starting..."

def init():

    parser = argparse.ArgumentParser(description = \
            "M/D/1 and M/D/1/K Queue Simulation")
    parser.add_argument('--arrival', action="store", default="M")
    parser.add_argument('--service', action="store", default="M")
    parser.add_argument('--num', action="store", default="1")
    parser.add_argument('--size', action="store", default="inf")
    parser.add_argument('--tickLen', action="store", default="1")
    parser.add_argument('--numOfTicks', action="store", default="100")

    # args is a type dict.
    argsDict = vars(parser.parse_args())

    # Init our processes.
    # TODO: Find a better way of doing this
    tickTockPID = multiprocessing.Process(target=tickTock, args=(argsDict['tickLen'], argsDict['numOfTicks']))
    genDataPID = multiprocessing.Process(target=genData)
    transmitterPID = multiprocessing.Process(target=transmitter, args='t')
    receiverPID = multiprocessing.Process(target=receiver, args='r')

    # Spawn our processes.
    # tickTockPID.start()
    genDataPID.start()
    transmitterPID.start()
    receiverPID.start()

    # Let it rip.
    main(argsDict)

if __name__ == '__main__':
    init()
