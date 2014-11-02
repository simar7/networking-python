#!/usr/bin/python
'''
    ECE 358: Computer Networks
    Project: CSMA/CD protocols
    Author:  Simarpreet Singh (s244sing@uwaterloo.ca)
             Louisa Chong (l5chong@uwaterloo.ca)

'''
import time
import sys
import argparse
import random
import logging
import Queue
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
NODES_SRC_LIST = []
NODES_SRC_TIME_DICT = {} # key:value <=> src_node_thread:tx_time
NODES_SRC_DEST_DICT = {} # key:value <=> src_node_thread:dst_node_thread
NODES_SRC_IDLE_DICT = {} # key:value <=> src_node_thread:idle_time
packet_dropped = 0
packet_transmitted = 0
packet_collided = 0
sender_threads = []
link_queue = []

GLOBAL_TICK = 0

class Packet:
    def __init__(self, sender, sender_index, send_time, destination):
        self.data = "fun"
        self.sender = sender
        self.sender_index = sender_index
        self.send_time = send_time
        self.destination = destination

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

# FIXME: @clouisa: Is this right?
def nextGenTime(current_tick):
    gen_tick = random.randint(0, TICK_DURATION)
    return int(gen_tick + current_tick)

# TODO: Qualify as a collision if the queue was found
# to have packets from two diff sources
def collisionDetector():
    # TODO: We could do this better with a lambda function.
    listOfSrcs = []
    for packet in list(link_queue.queue):
        listOfSrcs.append(packet.data)
    if len(set(listOfSrcs)) != len(listOfSrcs):
        logging.info("[%s]: Dupe found, Collision Detected!" % (collisionDetector.__name__))
        return True
    else:
        return False

# TODO: We probably need more logic than just popping elements
# to make the link clean.
def jammingSignal():
    for counter in xrange(0, len(link_queue)):
        global link_queue
        link_queue.pop()

# TODO: Create a Binary Exponential Backoff timer.
def BinaryBackoff():
    return True

# Returns true or false depending on if it's the right time to send.
def is_right_time(inputThread):
    if GLOBAL_TICK >= NODES_SRC_TIME_DICT[inputThread]:
        return True
    else:
        return False

def transmit_worker():
    while True:
        src_name = threading.currentThread().getName()
        src_idx = int(src_name[len(src_name)-1:])
        send_time = NODES_SRC_TIME_DICT[src_name]
        dst = NODES_SRC_DEST_DICT[src_name]
        newPacket = Packet(src_name, src_idx, send_time, dst)

        # 1-persistance case:
        if P_PRAM == 1:
            while newPacket.is_detected(src_idx, tick):
                logging.info("[%s]: Channel Busy, gadfly waiting.." % (src_name))

        # non-persistance case:
        elif P_PRAM == 2:
            while newPacket.is_detected(src_idx, tick):
                waitFor = randint(0, tick)
                logging.info("[%s]: Channel Busy, waiting for %s (random) time.." % (src_name, waitFor))
                time.sleep(waitFor)

        # TODO: p-persistance case:
        elif P_PRAM == 3:
            print "some other cool yet to be implemented logic"

        if (link_queue.qsize() == MAX_LINK_SIZE):
            logging.error("[%s]: Failed to transmit: src:%s | dest:%s" % \
                    (src_name, newPacket.sender, newPacket.destination))
            global packet_dropped
            packet_dropped += 1

        # Is it the right time for me as a thread to transmit?
        if is_right_time(src_name):
            logging.info("[%s]: Transmitting: src:%s | dest:%s" % \
                    (src_name, newPacket.sender, newPacket.destination))
            try:
                global link_queue
                link_queue.put(newPacket)
            except Exception as e:
                logging.error("[%s]: Exception was raised! msg: %s" % (src_name, e.message))
            finally:
                global packet_transmitted
                packet_transmitted += 1
                # Update for the next generation value for this thread.
                global NODES_SRC_TIME_DICT
                NODES_SRC_TIME_DICT[src_name] = nextGenTime(GLOBAL_TICK)
                if collisionDetector():
                    waitFor = random.randint(0, GLOBAL_TICK)
                    logging.warn("[%s]: Collision Detected, waiting for: %s ticks.."%\
                            (threading.currentThread().getName(), waitFor))
                    global packet_collided
                    packet_collided += 1
                    time.sleep(waitFor)
                    jammingSignal()
        else:
            logging.debug("[%s]: It's not the right time for me to transmit, so I'm gonna chill." % src_name)
            global NODES_SRC_IDLE_DICT
            NODES_SRC_IDLE_DICT[src_name] += 1


# The scheduler basically calculates randomly generated
# times at which each node in the system would act as a transmitter.
# This assigns an initial order in which the nodes should be acting as transmitters
# each time a node tranmits, it request for the nextGenTime()
# FIXME: Take into account the tick size for proper generation times.
def scheduler(sender_thread_list, current_tick):
    for node in sender_thread_list:
        global NODES_SRC_TIME_DICT
        # FIXME: Fix the random.random() to something that useful (Poisson distribution)
        NODES_SRC_TIME_DICT[node] = current_tick + random.random()
        # randomly schedule destinations for senders.
        global NODES_SRC_DEST_DICT
        NODES_SRC_DEST_DICT[node] = sender_thread_list[random.randint(0, len(sender_thread_list)-1)]

def tickTock():
    for tick in xrange(0, TOTAL_TICKS):
        global GLOBAL_TICK
        GLOBAL_TICK += TICK_DURATION

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

    global MAX_LINK_SIZE
    MAX_LINK_SIZE = LAN_SPEED * 8
    global link_queue
    link_queue = Queue.Queue(MAX_LINK_SIZE)

    # Each node is a possible sender and is a thread.
    for thread in xrange(0, SERVERS):
        t = threading.Thread(target=transmit_worker)
        global sender_threads
        sender_threads.append(t)
        global NODES_SRC_LIST
        NODES_SRC_LIST.append(t.getName())
        global NODES_SRC_TIME_DICT
        NODES_SRC_TIME_DICT[t.getName()] = 0
        global NODES_SRC_IDLE_DICT
        NODES_SRC_IDLE_DICT[t.getName()] = 0

    # Call the scheduler right now to determine times to send.
    scheduler(NODES_SRC_LIST, 0)

    for elem in NODES_SRC_TIME_DICT:
        print "%s : %s" % (elem, NODES_SRC_DEST_DICT[elem])

    # Start all the threads.
    for thread in xrange(0, SERVERS):
        sender_threads[thread].start()

    # Let it rip.
    main(argsDict)

if __name__ == '__main__':
    init()
