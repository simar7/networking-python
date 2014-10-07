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
import logging
import random
import argparse
import math
import Queue


class Packet:
    transmit_time = None

    def __init__(self, tick):
        self.transmit_time = tick


GEN_DIST = None
SERVE_DIST = None
TICK_DURATION = 0
LAMBDA = 0
TOTAL_TICKS = 0
PACKET_LEN = 0
SERVICE_RATE = 0
QUEUE_SIZE = 0


def tickTock():
    if (QUEUE_SIZE == "inf"):
        packet_queue = Queue.Queue()
    else:
        packet_queue = Queue.Queue(QUEUE_SIZE)

    # variables for collecting report data
    next_generation = None
    next_service = 0
    packet_in_queue = 0
    packet_sojourn = 0
    packet_transmitted = 0
    packet_received = 0
    packet_dropped = 0
    receiver_idle = 0

    for tick in xrange(0, TOTAL_TICKS):
        '''
        if (tick % 100000 == 0):
            print "[%s] current tick: %s" % (tickTock.__name__, tick)
        '''

        # Transmitter
        if next_generation == None:
            next_generation = nextGenTime(tick)
        if tick >= next_generation:
            is_dropped = transmitter(tick, packet_queue)
            packet_transmitted += 1
            if not is_dropped:
                packet_dropped += 1
            next_generation = nextGenTime(tick)
            logging.debug("[%s] next generation: %s" % (tickTock.__name__, next_generation))

        # Receiver
        if tick >= next_service:
            if packet_queue.empty():
                receiver_idle += 1
                next_service += 1
            else:
                next_service = nextServeTime(tick)
                packet = receiver(packet_queue)
                # sojorn time = queing time + service time
                packet_sojourn += (tick - packet.transmit_time + (next_service - tick))
                packet_received += 1
                logging.debug("[%s] next service: %s" % (tickTock.__name__, next_service))
        packet_in_queue += packet_queue.qsize()

    print "packet transmitted: %s" % packet_transmitted
    print "packet received: %s" % packet_received
    print "packet dropped: %s" % packet_dropped
    print "packet dropped percent: %s" % (packet_dropped * 100.0 / packet_transmitted)
    print "server idle: %s" % receiver_idle
    print "E[N]: %s" % (float(packet_in_queue) / TOTAL_TICKS)
    print "E[T]: %s" % (float(packet_sojourn) / packet_received)

def nextGenTime(current_tick):
    if GEN_DIST == 'M':
        gen_number = random.random()
        gen_time = (-1.0 / LAMBDA) * math.log(1 - gen_number)
        gen_tick = math.ceil(gen_time / TICK_DURATION)
        return int(gen_tick + current_tick)
    else:
        raise Exception("Unknown distribution")


def nextServeTime(current_tick):
    if SERVE_DIST == 'D':
        service_time = float(PACKET_LEN) / SERVICE_RATE
        service_tick = math.ceil(service_time / TICK_DURATION)
        return int(service_tick + current_tick)
    else:
        raise Exception("Unknown distribution")


def transmitter(tick, packet_queue):
    packet_data = Packet(tick)
    if (packet_queue.qsize() == QUEUE_SIZE):
        logging.error("[%s]: Failed to transmit: %s" % (transmitter.__name__, packet_data.transmit_time))
        return False
    else:
        logging.info("[%s]: Transmit: %s" % (transmitter.__name__, packet_data.transmit_time))
        packet_queue.put(packet_data)
        return True


def receiver(packet_queue):
    # This state should not occur
    if packet_queue.empty():
        logging.warning("[%s] Server is idle" % (receiver.__name__))
        return None
    else:
        packet = packet_queue.get()
        logging.info("[%s] Serve packet: %s" % (receiver.__name__, packet.transmit_time))
        return packet

def main(argv):
    print "Program is starting..."
    tickTock()


def init():
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    parser = argparse.ArgumentParser(description= \
                                         "M/D/1 and M/D/1/K Queue Simulation")
    # distribution of arrive time
    parser.add_argument('--generation', action="store", default="M")
    # didtribution of service time
    parser.add_argument('--service', action="store", default="M")
    # number of servers
    parser.add_argument('--num', action="store", type=int, default="1")
    # size of the queue
    parser.add_argument('--size', action="store", default="inf")
    # the tick intervals
    parser.add_argument('--tickLen', action="store", type=float, default="1.0")
    # number of ticks until the process ends
    parser.add_argument('--numOfTicks', action="store", type=int, default="100")
    # average number of packets generated per second
    parser.add_argument('--lambda', action="store", type=float, default="100.0")
    # packet length in bits
    parser.add_argument('-L', action="store", type=int, default="2000")
    # service time in bits per second
    parser.add_argument('-C', action="store", type=int, default="500")

    # args is a type dict.
    argsDict = vars(parser.parse_args())

    # fixed value for the program
    global TICK_DURATION
    TICK_DURATION = argsDict['tickLen']
    global TOTAL_TICKS
    TOTAL_TICKS = argsDict['numOfTicks']
    global LAMBDA
    LAMBDA = argsDict['lambda']
    global PACKET_LEN
    PACKET_LEN = argsDict['L']
    global SERVICE_RATE
    SERVICE_RATE = int(argsDict['C'])
    global QUEUE_SIZE
    if argsDict['size'] == 'inf':
        QUEUE_SIZE = "inf"
    else:
        int(argsDict['size'])
    global GEN_DIST
    GEN_DIST = argsDict['generation']
    global SERVE_DIST
    SERVE_DIST = argsDict['service']

    # Let it rip.
    main(argsDict)


if __name__ == '__main__':
    init()
