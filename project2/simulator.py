#!/usr/bin/python
'''
    ECE 358: Computer Networks
    Project: CSMA/CD protocols
    Author:  Simarpreet Singh (s244sing@uwaterloo.ca)
             Louisa Chong (l5chong@uwaterloo.ca)

'''
import sys
import argparse
import random
import logging
import threading
from threading import Thread, Lock

SERVERS = 0
ARRIVAL_RATE = 0
LAN_SPEED = 0
PACKET_LEN = 0
PERSISTANCE = 0
TOTAL_TICKS = 0
MAX_LINK_SIZE = 0
NODE_LOCATION_ARR = []
mutex = Lock()

class Packet():
    def __init__(self, src, dst):
        self.data = "cool-stuff"
        self.source = src
        self.destination = dst

def src_dest_picker(node_list):
    src = random.randint(0, len(node_list)-1)
    dst = random.randint(0, len(node_list)-1)
    # unlikely to happen
    if src == dst:
        dst = random.randint(0, len(node_list)-1)
    return ([src, dst])

def nextGenTime(current_tick):
    gen_number = random.randint(0, 10)
    return int(gen_tick + current_tick)

# TODO: Qualify as a collision if the queue was found
# to have packets from two diff sources
def collisionDetector(link_queue):
    # TODO: We could do this better with a lambda function.
    listOfSrcs = []
    for src in link_queue:
        listOfSrc.append(src.data)
    if len(set(listOfSrcs)) != len(listOfSrcs):
        logging.info("[%s]: Collision Detected!: %s" % (transmitter.__name__)
        return True
    else:
        return False

# TODO: We probably need more logic than just popping elements
# to make the link clean.
def jammingSignal(link_queue):
    for counter in xrange(0, len(link_queue)):
        link_queue.pop()

# TODO: Create a Binary Exponential Backoff timer.
def BinaryBackoff():
    return True

def transmit_worker(tick, src, dst, link_queue):
    while True:
    # 1-persistance case:
    if PERSISTANCE == 1:
        while mutex_locked():
            logging.info("[%s]: Channel Busy, gadfly waiting.." % (transmit_worker.__name__)

    # non-persistance case:
    elif PERSISTANCE == 2:
        while mutex_locked():
            waitFor = randint(0, tick)
            logging.info("[%s]: Channel Busy, waiting for %s (random) time.." % (transmit_worker.__name__, waitFor)
            time.sleep(waitFor)

    # TODO: p-persistance case:
    elif PERSISTANCE == 3:
        print "some other cool yet to be implemented logic"

    newPacket = Packet(src, dst)
    if (link_queue.qsize() == MAX_LINK_SIZE):
        logging.error("[%s]: Failed to transmit: src:%s | dest:%s" % \
                (transmit_worker.__name__, newPacket.source, newPacket.destination))
        packet_dropped += 1
    else:
        logging.info("[%s]: Transmitting: src:%s | dest:%s" % \
                (transmit_worker.__name__, newPacket.source, newPacket.destination))
        mutex.acquire()
        try:
            link_queue.put(newPacket)
        finally:
            mutex.release()
            packet_transmitted += 1

    if collisionDetector(link_queue):
        waitFor = randint(0, tick)
        logging.warn("[%s]: Collision Detected, waiting for: %s ticks.."%\
                (transmit_worker.__name__, waitFor)
        packet_collided += 1
        time.sleep(waitFor)

def tickTock():
    global MAX_LINK_SIZE
    MAX_LINK_SIZE = LAN_SPEED * 8
    link_queue = Queue.Queue(MAX_LINK_SIZE)

    for tick in xrange(0, TOTAL_TICKS):
        src_node, dst_node = src_dst_picker(NODE_LOCATION_ARR)

        # Select-and-Transmit Logic
        if src_next_gen_time == None:
            src_next_gen_time = nextGenTime(tick)
        if tick >= src_next_gen_time:
            tx_ret = transmit_data(tick, src_node, dst_node, link_queue)
            packet_transmitted += 1
            if not tx_ret:
                packet_dropped += 1
            src_next_gen_time = nextGenTime(tick)
            is_Collision = collisionDetector(link_queue)
            if is_Collision:
                packet_collided += 1
                jammingSignal(link_queue)

        # Timely receive logic
        if tick >= next_service:
def ONE_persistance():
    if channelIdle():


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
    # packet length in bits (default = 1500bytes)
    parser.add_argument('-L', action="store", type=int, default="6000")
    # persistence parameter
    parser.add_argument('-P', action="store", type=float, default="1")
    # total amount of time to run
    parser.add_argument('-T', action="store", type=int, default="10000")

    # args is a type dict.
    argsDict = vars(parser.parse_args())

    global SERVERS
    SERVERS = argsDict['N']
    global ARRIVAL_RATE
    ARRIVAL_RATE = argsDict['A']
    global LAN_SPEED
    LAN_SPEED    = argsDict['W']
    global PACKET_LEN
    PACKET_LEN   = argsDict['L']
    global PERSISTANCE
    PERSISTANCE  = argsDict['P']
    global TOTAL_TICKS
    TOTAL_TICKS = argsDict['T']
    global NODE_LOCATION_ARR
    NODE_LOCATION_ARR = NODE_LOCATION_ARR.extend(xrange(SERVERS))

    # Let it rip.
    main(argsDict)

if __name__ == '__main__':
    init()
