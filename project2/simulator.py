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

SERVERS           = 0
ARRIVAL_RATE      = 0
LAN_SPEED         = 0
PACKET_LEN        = 0
TOTAL_TICKS       = 0
P_PARM            = "1"
ETHERNET_SPEED    = 2e8
TICK_DURATION     = 0
D_TRANS           = 0
D_TOTAL_PROP      = 0
MAX_LINK_SIZE     = 0
SENSE_MEDIUM_TIME = 0
JAMMING_TIME      = 0

# BEB Params
K_MAX = 10
T_P = 0

NODES_SRC_LIST      = []
NODES_SRC_CLK_DICT  = {} # key:value <=> node:current_tick
NODES_SRC_TIME_DICT = {} # key:value <=> src_node_thread:tx_time
NODES_SRC_DEST_DICT = {} # key:value <=> src_node_thread:dst_node_thread
NODES_SRC_IDLE_DICT = {} # key:value <=> src_node_thread:idle_time
NODES_EXP_BACKOFF   = {} # key:value <=> node:{i: index, Tb : wait_time}
mutex               = Lock()
sender_threads      = []
link_queue          = []
GLOBAL_TICK         = 0

# Data Collection
packet_dropped      = 0
packet_transmitted  = 0
packet_collided     = 0
CALC = None
throughput = 0
avgDelay = 0

class Packet:
    def __init__(self, sender, sender_index, send_time, jamming = False):
        self.data = "fun"
        self.jamming = jamming
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

def dequeue_helper():
    for packet in link_queue:
        packet_trans_dist = max(packet.sender_index, D_TOTAL_PROP - packet.sender_index)
        if ((packet.jamming and (GLOBAL_TICK >= packet.send_time + packet_trans_dist + JAMMING_TIME))
         or (not packet.jamming and (GLOBAL_TICK >= packet.send_time + packet_trans_dist + D_TRANS))):
                link_queue.remove(packet)
                logging.info("[Dequeue] current time: %s, sender: %s, send_time: %s" % (GLOBAL_TICK, packet.sender, packet.send_time))

def next_gen_time(current_tick):
    gen_number = random.random()
    gen_time = (-1.0 / ARRIVAL_RATE) * math.log(1 - gen_number)
    gen_tick = math.ceil(gen_time / TICK_DURATION)
    return int(gen_tick + current_tick)

# return true when the node detects any signal from other sources
# medium is either busy or theres an collision
def is_medium_busy(from_index):
    for packet in link_queue:
        if packet.sender_index != from_index:
            if packet.is_detected(from_index, GLOBAL_TICK):
                return True
    return False

def binary_backoff(src):
    K_MAX = 10
    i = 0
    t_b = 0
    node_history = None
    if src in NODES_EXP_BACKOFF:
        node_history = NODES_EXP_BACKOFF[src]
        i = node_history['i']
        t_b = node_history['t_b']
    i += 1
    #NOTE: this is the error state, the associated packet should be dropped
    if i > K_MAX:
        return 0
    T_b = random.randint(0, math.pow(2, i) -1) * T_P
    NODES_EXP_BACKOFF[src] = {'i': i, 't_b': T_b}
    return T_b

# Returns true or false depending on if it's the right time to send.
def is_right_time(inputThread):
    logging.debug("[%s]: Thread:%s has a send time of: %s ticks" % \
            (is_right_time.__name__, inputThread, NODES_SRC_TIME_DICT[inputThread]))
    logging.debug("[%s]: Thread:%s Current Tick: %s" % (is_right_time.__name__, inputThread,NODES_SRC_CLK_DICT[inputThread]))
    if NODES_SRC_CLK_DICT[inputThread] >= NODES_SRC_TIME_DICT[inputThread]:
        return True
    else:
        return False

def transmit_worker():
    BEB_ret = 0
    src_name = threading.currentThread().getName()
    send_time = NODES_SRC_TIME_DICT[src_name]
    src_idx = math.ceil(NODES_SRC_LIST.index(src_name) * 10 / (ETHERNET_SPEED*TICK_DURATION))
    newPacket = None
    # TODO: Do we really need this assignment?
    current_time = GLOBAL_TICK
    while (current_time < TOTAL_TIME):
        send_time = NODES_SRC_TIME_DICT[src_name]
        # generate a new packet after getting an error in binary exponential backoff
        if (BEB_ret == 0):
            newPacket = Packet(src_name, src_idx, send_time)
            # Generated a new packet deliver time

        # a tick passed by
        current_tick = GLOBAL_TICK
        if (NODES_SRC_CLK_DICT[src_name] != current_tick):
            NODES_SRC_CLK_DICT[src_name] = current_tick

            # Is it the right time for me as a thread to transmit?
            if is_right_time(src_name):

                logging.debug("[%s]: Starting Medium Sensing for 96 bit time" % (src_name))
                sense_time = 0
                # 1-persistance case:
                if P_PRAM == '1':
                    # this will sense if the medium is free for 96 bit time
                    while sense_time < SENSE_MEDIUM_TIME:
                        # 1 tick has passed
                        current_tick = GLOBAL_TICK
                        if current_tick != NODES_SRC_CLK_DICT[src_name]:
                            NODES_SRC_CLK_DICT[src_name] += 1
                            if is_medium_busy(src_idx):
                                sense_time = 0
                                logging.debug("[%s]: Channel Busy, Restarting carrier sensing.." % (src_name))
                            else:
                                sense_time += 1

                # TODO: update logic to make sure medium sensing takes 96 bit time
                # non-persistance case:
                elif P_PRAM == '2':
                    while newPacket.is_detected(src_idx, tick):
                        waitFor = next_gen_time(GLOBAL_TICK)
                        logging.debug("[%s]: Channel Busy, waiting for %s (random) time.." % (src_name, waitFor))
                        time.sleep(waitFor)


                # TODO: p-persistance case:
                elif P_PRAM != '1' and P_PRAM != '2':
                    print "some other cool yet to be implemented logic"

                logging.debug("[%s]: Medium Sensing completed, start to transmit" % (src_name))

                logging.info("[%s]: Transmitting packet at tick %s" % (src_name, current_tick))
                try:
                    link_queue.append(newPacket)
                except Exception as e:
                    logging.error("[%s]: Exception was raised! msg: %s" % (src_name, e.message))
                finally:
                    transmit_time = 0
                    collision_detected = False
                    is_jammed = False
                    while ((transmit_time < D_TRANS) and (collision_detected == False) and (is_jammed == False)):
                        # 1 tick has passed
                        current_tick = GLOBAL_TICK
                        if NODES_SRC_CLK_DICT[src_name] != current_tick:
                            NODES_SRC_CLK_DICT[src_name] += 1
                            # jamming signal detected
                            is_jammed = False
                            for packet in link_queue:
                                if (packet.jamming and (packet.sender != src_name)):
                                    # abort current transmission
                                    is_jammed = True
                                    try:
                                        link_queue.remove(newPacket)
                                    except Exception as e:
                                        logging.debug("[%s]: Nothing to remove, safe. | ret_msg: %s" % (src_name, e.message))
                                    BEB_ret = 0
                                    NODES_SRC_TIME_DICT[src_name] = next_gen_time(current_tick)
                                    logging.info("[%s]: signal jammed" % (src_name))
                                    logging.info("[%s]: next_gen at: %s" % (src_name, NODES_SRC_TIME_DICT[src_name]))
                            if not is_jammed:
                                # collision detected
                                collision_detected = is_medium_busy(src_idx)
                                if collision_detected:
                                    transmit_time = 0
                                    try:
                                        if newPacket in link_queue:
                                            link_queue.remove(newPacket)
                                    except Exception as e:
                                        logging.debug("[%s]: Nothing to remove, safe. | ret_msg: %s" % (src_name, e.message))
                                    newPacket = Packet(src_name, src_idx, send_time, True)
                                    # transmit jamming signal for 48 bit time
                                    while (transmit_time < JAMMING_TIME):
                                        current_tick = GLOBAL_TICK
                                        if current_tick != NODES_SRC_CLK_DICT[src_name]:
                                            NODES_SRC_CLK_DICT[src_name] += 1
                                            transmit_time += 1
                                    logging.info("[%s]: Collision Detected, going through binary exponential backoff"%\
                                            (threading.currentThread().getName()))
                                    global packet_collided
                                    packet_collided += 1
                                    # binary exponential backoff
                                    BEB_ret = binary_backoff(src_name)
                                    if BEB_ret == 0:
                                        global packet_dropped
                                        packet_dropped += 1
                                    else:
                                        global NODES_SRC_IDLE_DICT
                                        NODES_SRC_IDLE_DICT[src_name] = NODES_SRC_IDLE_DICT[src_name] + BEB_ret
                                else:
                                    logging.debug("[%s] packet transmition for %s ticks" % (src_name, transmit_time))
                                    transmit_time += 1

                    if (transmit_time >= D_TRANS):
                        logging.debug("[%s] packet transmitted")
                        BEB_ret = 0
                        global packet_transmitted
                        packet_transmitted += 1
                        NODES_SRC_TIME_DICT[src_name] = next_gen_time(current_tick)
                        logging.info("[%s]: next_gen at: %s" % (src_name, NODES_SRC_TIME_DICT[src_name]))

            else:
                logging.debug("[%s]: It's not the right time for me to transmit, so I'm gonna chill." % src_name)
                NODES_SRC_IDLE_DICT[src_name] += 1

# The schedule basically calculates randomly generated
# times at which each node in the system would act as a transmitter.
# This assigns an initial order in which the nodes should be acting as transmitters
# each time a node tranmits, it request for the next_gen_time()
# FIXME: Take into account the tick size for proper generation times.
def scheduler(sender_thread_list, current_tick):
    for node in sender_thread_list:
        global NODES_SRC_TIME_DICT
        NODES_SRC_TIME_DICT[node] = next_gen_time(current_tick)
        logging.info("[%s]: next gen at: %s" % (node, NODES_SRC_TIME_DICT[node]))

def nerdystats():
    logging.info("[%s]: packets transmitted: %s" % (nerdystats.__name__, packet_transmitted))
    logging.info("[%s]: packets collided   : %s" % (nerdystats.__name__, packet_collided))
    logging.info("[%s]: packets dropped    : %s" % (nerdystats.__name__, packet_dropped))

    for node in NODES_SRC_LIST:
        logging.debug("[%s]: Node #%s had idle time: %s ticks of fun time." %\
                (nerdystats.__name__, node, NODES_SRC_IDLE_DICT[node]))

    if CALC == 'throughput':
        logging.info("[%s]: Throughput    : %s" % (nerdystats.__name__, throughput))
        logging.debug("[%s]: Average Delay : %s" % (nerdystats.__name__, avgDelay))
    if CALC == 'avgDelay':
        logging.info("[%s]: Average Delay : %s" % (nerdystats.__name__, avgDelay))
        logging.debug("[%s]: Throughput    : %s" % (nerdystats.__name__, throughput))
    if CALC == 'both':
        logging.info("[%s]: Average Delay : %s" % (nerdystats.__name__, avgDelay))
        logging.info("[%s]: Throughput    : %s" % (nerdystats.__name__, throughput))
    else:
        logging.error("[%s]: Invalid Calculation parameter" % (nerdystats.__name__))

def tickTock():
    global GLOBAL_TICK
    GLOBAL_TICK = 0
    while GLOBAL_TICK < TOTAL_TICKS-1:
        # clock synchronization across all nodes
        all_updated = True
        for nodes in NODES_SRC_CLK_DICT:
            if NODES_SRC_CLK_DICT[nodes] != GLOBAL_TICK:
                all_updated = False
        if all_updated:
            GLOBAL_TICK += 1
            if (GLOBAL_TICK % 100 == 0):
                logging.info("[%s]: current global tick at: %s" % (tickTock.__name__, GLOBAL_TICK))
            dequeue_helper()

def main(argv):
    print "Program is starting..."

    # Start all the threads.
    [thread.start() for thread in sender_threads]
    tickTock()
    [thread.join() for thread in sender_threads]
    nerdystats()

def init():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    parser = argparse.ArgumentParser(description= \
            "CSMA/CA protocols")

    # number of computers
    parser.add_argument('-N', action="store", type=int, default="10")
    # average arrival rate packets per second
    parser.add_argument('-A', action="store", type=float, default="5")
    # speed of Lan in bits per second (default = 1Mbps)
    parser.add_argument('-W', action="store", type=int, default="1000000")
    # packet length in bits (default = 1500bytes = 12000bits)
    parser.add_argument('-L', action="store", type=int, default="12000")
    # persistence parameter
    parser.add_argument('-P', action="store", type=str, default="1")
    # the tick intervals (seconds)
    parser.add_argument('--tickLen', action="store", type=float, default="1e-5")
    # total amount of time to run
    parser.add_argument('-T', action="store", type=int, default="100000")
    # what is being calculated, to pass to nerdyStats for relevant stats.
    parser.add_argument('--calc', action="store", type=str, default='throughput')

    # args is a type dict.
    argsDict = vars(parser.parse_args())

    global SERVERS
    SERVERS       = argsDict['N']
    global ARRIVAL_RATE
    ARRIVAL_RATE  = argsDict['A']
    global LAN_SPEED
    LAN_SPEED     = argsDict['W']
    global PACKET_LEN
    PACKET_LEN    = argsDict['L']
    global P_PRAM
    P_PRAM        = argsDict['P']
    global TOTAL_TICKS
    TOTAL_TICKS   = argsDict['T']
    # fixed value for the program
    global TICK_DURATION
    TICK_DURATION = argsDict['tickLen']
    global CALC
    CALC = argsDict['calc']

    '''
    one time calculation
    '''
    global TOTAL_TIME
    TOTAL_TIME        = TICK_DURATION * TOTAL_TICKS
    # the total ticks it take for a full packet to be transmitted
    global D_TRANS
    D_TRANS           = math.ceil(PACKET_LEN/(LAN_SPEED*TICK_DURATION))
    logging.info("[%s]: Transmission Delay: %s" % (init.__name__, D_TRANS))
    # the total ticks it take for a packet to be propagated
    # from the first node to the last node
    global D_TOTAL_PROP
    D_TOTAL_PROP      = math.ceil((10*(SERVERS-1)) / (ETHERNET_SPEED*TICK_DURATION))
    logging.info("[%s]: Total Propagation Delay: %s" % (init.__name__, D_TOTAL_PROP))
    # 512 bit time in ticks
    global T_P
    T_P               = math.ceil(512/(LAN_SPEED*TICK_DURATION))
    global MAX_LINK_SIZE
    MAX_LINK_SIZE     = LAN_SPEED * 8
    # convert 96 bit time to ticks
    global SENSE_MEDIUM_TIME
    SENSE_MEDIUM_TIME = math.ceil(96/(LAN_SPEED*TICK_DURATION))
    logging.info("[%s]: Sense Medium Time: %s" % (init.__name__, SENSE_MEDIUM_TIME))
    # convert 48 bit time to ticks
    global JAMMING_TIME
    JAMMING_TIME = math.ceil(48/(LAN_SPEED*TICK_DURATION))
    logging.info("[%s]: Jamming Time: %s" % (init.__name__, JAMMING_TIME))
    '''
    initiate date for the nodes
    '''

    # Each node is a possible sender and is a thread.
    for thread in xrange(0, SERVERS):
        t = threading.Thread(target=transmit_worker)
        t.setDaemon(True)
        global sender_threads
        sender_threads.append(t)
        global NODES_SRC_CLK_DICT
        NODES_SRC_CLK_DICT[t.getName()] = 0
        global NODES_SRC_LIST
        NODES_SRC_LIST.append(t.getName())
        global NODES_SRC_TIME_DICT
        NODES_SRC_TIME_DICT[t.getName()] = 0
        global NODES_SRC_IDLE_DICT
        NODES_SRC_IDLE_DICT[t.getName()] = 0

    # Call the scheduler right now to determine times to send.
    scheduler(NODES_SRC_LIST, 0)

    # Let it rip.
    main(argsDict)

if __name__ == '__main__':
    init()
