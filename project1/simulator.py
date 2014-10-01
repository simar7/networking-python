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
import math
import Queue

'''
Pre-defined constants
updated in init when user enter parameter
'''
# the distribution for the generation
GEN_DIST      = 'M'
# the distribution for the service
SERVE_DIST    = 'D'
# the tick intervals
TICK_DURATION = 1
# average number
LAMBDA        = 1
# total ticks
TOTAL_TICKS   = 100
# packet length in bits
PACKET_LEN    = 2000
# service time for each packet per second
SERVICE_RATE  = 500
# the size of the queue
QUEUE_SIZE    = 'inf'

def tickTock():
    # define the queue for the simulation
    if (QUEUE_SIZE == "inf"):
        packet_queue = Queue.Queue()
    else:
        packet_queue = Queue.Queue(QUEUE_SIZE)

    next_generation = None
    next_service =  0
    for tick in xrange(0, TOTAL_TICKS):
        print "[%s] current tick: %s" % (tickTock.__name__, tick)
        # Transmitter
        if next_generation == None:
            next_generation = nextGenTime(tick)
        if tick >= next_generation:
            transmitter(packet_queue)
            next_generation = nextGenTime(tick)
            print "[%s] next generation: %s" % (tickTock.__name__, next_generation)
        # Receiver
        if tick >= next_service:
            if packet_queue.empty():
                next_service += 1
            else:
                receiver(packet_queue)
                next_service = nextServeTime(tick)
                print "[%s] next service: %s" % (tickTock.__name__, next_service)
        # Receiver

def nextGenTime(current_tick):
    if GEN_DIST == 'M':
        gen_number = random.random()
        gen_time = (-1/LAMBDA)*math.log(1-gen_number)
        gen_tick = math.ceil(gen_time/TICK_DURATION)
        return (gen_tick + current_tick)
    else:
        raise Exception("Unknown distriution")

def nextServeTime(current_tick):
    if SERVE_DIST == 'D':
        service_time = int(PACKET_LEN)/int(SERVICE_RATE)
        service_tick = math.ceil(service_time/int(TICK_DURATION))
        return (service_tick + current_tick)
    else:
        raise Exception("Unknown distribution")


def transmitter(packet_queue):
    packet_data = "packet"
    if packet_queue.full():
        print "[%s]: Failed to transmit: %s" % (transmitter.__name__, packet_data)
        return False
    else:
        print "[%s]: Transmit: %s" % (transmitter.__name__, packet_data)
        packet_queue.put(packet_data)
        return True

def receiver(packet_queue):
    # This state should not occur
    if packet_queue.empty():
        print "[%s] Server is idle" % (receiver.__name__)
        return False
    else:
        print "[%s] Serve packet: %s" % (receiver.__name__, packet_queue.get())
        return True

def main(argv):
    print "Program is starting..."
    tickTock()

def init():
    parser = argparse.ArgumentParser(description = \
            "M/D/1 and M/D/1/K Queue Simulation")
    # distribution of arrive time
    parser.add_argument('--generation', action="store", default="M")
    # didtribution of service time
    parser.add_argument('--service', action="store", default="M")
    # number of servers
    parser.add_argument('--num', action="store", default="1")
    # size of the queue
    parser.add_argument('--size', action="store", default="inf")
    # the tick intervals
    parser.add_argument('--tickLen', action="store", default="1")
    # number of ticks until the process ends
    parser.add_argument('--numOfTicks', action="store", default="100")
    # average number of packets generated per second
    parser.add_argument('--lambda', action="store", default="1")
    # packet length in bits
    parser.add_argument('-L', action="store", default="2000")
    # service time in bits per second
    parser.add_argument('-C', action="store", default="500")

    # args is a type dict.
    argsDict = vars(parser.parse_args())

    # fixed value for the program
    global TICK_DURATION
    TICK_DURATION = float(argsDict['tickLen'])
    global TOTAL_TICKS
    TOTAL_TICKS = int(argsDict['numOfTicks'])
    global LAMBDA
    LAMBDA = float(argsDict['lambda'])
    global PACKET_LEN
    PACKET_LEN = int(argsDict['L'])
    global SERVICE_RATE
    REVICE_RATE = argsDict['C']
    global QUEUE_SIZE
    QUEUE_SIZE = argsDict['size']

    # Let it rip.
    main(argsDict)

if __name__ == '__main__':
  init()
