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
NODE_TIMINGS_ARR = []
NODES_KEY_TIME_DICT = {} # key:value <=> node#:tx_time
mutex = Lock()

packet_dropped = 0
packet_transmitted = 0
packet_collided = 0

class Packet():
    def __init__(self, src, dst):
        self.data = "cool-stuff"
        self.source = src
        self.destination = dst

'''
We may not need this..
def src_dst_picker(node_list):
    src = random.randint(0, len(node_list)-1)
    dst = random.randint(0, len(node_list)-1)
    # unlikely to happen
    if src == dst:
        dst = random.randint(0, len(node_list)-1)
    return ([src, dst])
'''

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
        logging.info("[%s]: Collision Detected!: %s" % (transmitter.__name__))
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
                logging.info("[%s]: Channel Busy, gadfly waiting.." % (transmit_worker.__name__))

        # non-persistance case:
        elif PERSISTANCE == 2:
            while mutex_locked():
                waitFor = randint(0, tick)
                logging.info("[%s]: Channel Busy, waiting for %s (random) time.." % (transmit_worker.__name__, waitFor))
                time.sleep(waitFor)

        # TODO: p-persistance case:
        elif PERSISTANCE == 3:
            print "some other cool yet to be implemented logic"

        newPacket = Packet(src, dst)
        if (link_queue.qsize() == MAX_LINK_SIZE):
            logging.error("[%s]: Failed to transmit: src:%s | dest:%s" % \
                    (transmit_worker.__name__, newPacket.source, newPacket.destination))
            global packet_dropped
            packet_dropped += 1
        else:
            logging.info("[%s]: Transmitting: src:%s | dest:%s" % \
                    (transmit_worker.__name__, newPacket.source, newPacket.destination))
            mutex.acquire()
            try:
                link_queue.put(newPacket)
            finally:
                mutex.release()
                global packet_transmitted
                packet_transmitted += 1

        if collisionDetector(link_queue):
            waitFor = randint(0, tick)
            logging.warn("[%s]: Collision Detected, waiting for: %s ticks.."%\
                    (transmit_worker.__name__, waitFor))
            global packet_collided
            packet_collided += 1
            time.sleep(waitFor)

# The scheduler basically calculates randomly generated
# times at which each node in the system would act as a transmitter.
# This assigns an initial order in which the nodes should be acting as transmitters
# each time a node tranmits, it request for the nextGenTime()
# FIXME: Take into account the tick size for proper generation times.
def scheduler(node_array, current_tick):
    for node in xrange(0, len(node_array)):
        global NODES_KEY_TIME_DICT
        # FIXME: Fix the random.random() to something that useful (Poisson distribution)
        NODES_TIMINGS_ARR[node] = current_tick + random.random()

    # Now re-create a list of nodes that will be in order of execution.
    node_tx_list = sorted(NODES_KEY_TIME_DICT, key=NODES_KEY_TIME_DICT.get)
    return node_tx_list

def tickTock():
    global MAX_LINK_SIZE
    MAX_LINK_SIZE = LAN_SPEED * 8
    link_queue = Queue.Queue(MAX_LINK_SIZE)

    # First time scheduling to tick = 0
    inorder_exec_list = scheduler(NODE_LOCATION_ARR, 0)

    current_node = 0
    for tick in xrange(0, TOTAL_TICKS):
        #src_node, dst_node = src_dst_picker(NODE_LOCATION_ARR)
        if tick >= NODES_KEY_TIME_DICT[inorder_exec_list[current_node]]:
            tx_ret = transmit_data(tick, src_node, dst_node, link_queue)
            global packet_transmitted
            packet_transmitted += 1
            if not tx_ret:
                global packet_dropped
                packet_dropped += 1
            global NODES_KEY_TIME_DICT
            # Update the current node's value for next generation.
            # and increment the current_node counter to point to the next node.
            NODES_KEY_TIME_DICT[current_node] = nextGenTime(tick)
            current_node += 1

            # If we have transmitted atleast once from each node
            # Need to call the scheduler again to re-calc all new transmit times.
            if current_node >= len(NODES_KEY_TIME_DICT):
                inorder_exec_list = scheduler(NODE_LOCATION_ARR, tick)

            is_Collision = collisionDetector(link_queue)
            if is_Collision:
                global packet_collided
                packet_collided += 1
                jammingSignal(link_queue)

        # Timely receive logic
        # TODO: Needs @clouisa 's logic for determining the speed of packet transmission.
        # TODO: Also need logic for dequeueing from the link IF AND ONLY IF all nodes have
        # had the chance of listening to the message once.

def main(argv):
    print "Program is starting..."
    tickTock()

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
    global NODE_TIMINGS_ARR
    NODE_TIMINGS_ARR = [0] * SERVERS
    global NODES_KEY_TIME_DICT
    for node in xrange(0, SERVERS):
        NODES_KEY_TIME_DICT[node] = 0

    # Let it rip.
    main(argsDict)

if __name__ == '__main__':
    init()
