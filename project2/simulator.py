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
import math
import threading
from threading import Thread, Lock

SERVERS         = 0
ARRIVAL_RATE    = 0
LAN_SPEED       = 0
PACKET_LEN      = 0
TOTAL_TICKS     = 0
P_PARM          = "1"
ETHERNET_SPEED  = 2e10
TICK_DURATION   = 0
D_TRANS         = 0
D_TOTAL_PROP    = 0
MAX_LINK_SIZE   = 0
NODE_LOCATION_ARR = []
NODE_TIMINGS_ARR = []
NODES_KEY_TIME_DICT = {} # key:value <=> node#:tx_time

packet_dropped = 0
packet_transmitted = 0
packet_collided = 0

class Packet:
    def __init__(self, sender, sender_index, send_time):
        self.sender = sender
        self.sender_index = sender_index
        self.send_time = send_time

    def is_detected(self, from_index, current_tick):
        """ Check if the the packet can be sensed from the given index
        Keyword arguments:
        @from_index: index where they are sending from
        @current_tick: current time of the simulation (in ticks)
        """
        # how much time has passed
        time_passed = current_tick - self.send_time
        # how far did the signal propagate to on the smaller index side
        min_index = self.sender_index - time_passed
        # how far did the signal propagate to on the larger index side
        max_index = self.sender_index + time_passed
        # determine if the packet is detected
        if (((max_index >= from_index) and (from_index > self.sender_index))
         or ((min_index <= from_index) and (from_index <= self.sender_index))):
            return True
        return False

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
    newPacket = Packet(src, dst)

    # 1-persistance case:
    if P_PRAM == 1:
        while newPacket.is_detected(src, tick):
            logging.info("[%s]: Channel Busy, gadfly waiting.." % (transmit_worker.__name__))

    # non-persistance case:
    elif P_PRAM == 2:
        while newPacket.is_detected(src, tick):
            waitFor = randint(0, tick)
            logging.info("[%s]: Channel Busy, waiting for %s (random) time.." % (transmit_worker.__name__, waitFor))
            time.sleep(waitFor)

    # TODO: p-persistance case:
    elif P_PRAM == 3:
        print "some other cool yet to be implemented logic"

    if (link_queue.qsize() == MAX_LINK_SIZE):
        logging.error("[%s]: Failed to transmit: src:%s | dest:%s" % \
                (transmit_worker.__name__, newPacket.source, newPacket.destination))
        global packet_dropped
        packet_dropped += 1
    else:
        logging.info("[%s]: Transmitting: src:%s | dest:%s" % \
                (transmit_worker.__name__, newPacket.source, newPacket.destination))
        try:
            link_queue.put(newPacket)
        except Exception as e
            logging.error("[%s]: Exception was raised! msg: %s" % (transmit_worker.__name__, e.message))
        finally:
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

    # First time scheduling at tick = 0
    inorder_exec_list = scheduler(NODE_LOCATION_ARR, 0)

    current_node = 0
    for tick in xrange(0, TOTAL_TICKS):
        # it's time to transmit:
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

            # check at every tick if there was a collision
            # FIXME: I don't think this is the right logic, @clouisa to add.
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
    parser.add_argument('-P', action="store", type=str, default="1")
    # the tick intervals
    parser.add_argument('--tickLen', action="store", type=float, default="1.0")
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
    global P_PRAM
    P_PRAM = argsDict['P']

    global TOTAL_TICKS
    TOTAL_TICKS = argsDict['T']
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
