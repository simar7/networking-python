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

NODES_SRC_LIST       = []
nodes_src_clk_dict   = {} # key:value <=> node:current_tick
nodes_src_time_dict  = {} # key:value <=> src_node_thread:tx_time
nodes_src_idle_dict  = {} # key:value <=> src_node_thread:idle_time
nodes_src_sense_dict = {} # key:valie <=> src_node_thread:medium sensing time
nodes_exp_backoff    = {} # key:value <=> node:{i: index, Tb : wait_time}
sender_threads       = []
link_queue           = []
global_tick          = 0

# Data Collection
packet_dropped      = 0
packet_transmitted  = 0
packet_collided     = 0
CALC = None
throughput = 0
avgDelay = 0

"""
Useful Object
"""

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
        return (((max_index >= from_index) and (from_index > self.sender_index))
         or ((min_index <= from_index) and (from_index <= self.sender_index)))

    def is_fully_transmitted(self, current_tick):
        """ Check if the packet is fully transmitted
        Note: this does not take into account of the propagation delay
        This only show that
        Keyword arguement:
        """
        if self.jamming:
            return ((current_tick - self.send_time) >= JAMMING_TIME)
        else:
            return ((current_tick - seld.send_time) >= D_TRANS)

"""
Helper Functions
"""

def get_probability():
    return random.uniform(0, 2.0 * float(P_PRAM))

def dequeue_helper():
    for packet in link_queue:
        packet_trans_dist = max(packet.sender_index, D_TOTAL_PROP - packet.sender_index)
        # jamming packet take 48 bit time to transmit + propagation delay
        if packet.jamming:
            if global_tick >= packet.send_time + packet_trans_dist + JAMMING_TIME:
                try:
                    logging.info("[%s] Jamming signal from sender %s" %\
                        (dequeue_helper.__name__, packet.sender))
                    link_queue.remove(newpacket)
                except Exception as e:
                    logging.debug("[%s]: nothing to remove, safe. | ret_msg: %s" %\
                        (src_name, e.message))
        else:
            if (global_tick >= packet.send_time + packet_trans_dist + D_TRANS):
                try:
                    logging.info("[%s] Packet from sender %s" %\
                            (dequeue_helper.__name__, packet.sender))
                    link_queue.remove(newpacket)
                except Exception as e:
                    logging.debug("[%s]: nothing to remove, safe. | ret_msg: %s" %\
                        (src_name, e.message))

def next_gen_time(current_tick):
    gen_number = random.random()
    gen_time = (-1.0 / ARRIVAL_RATE) * math.log(1 - gen_number)
    gen_tick = math.ceil(gen_time / TICK_DURATION)
    return int(gen_tick + current_tick)

# Returns the time the source will need to wait before attempting to retransmit
def binary_backoff(src):
    K_MAX = 10
    i = 0
    t_b = 0
    node_history = None
    global nodes_exp_backoff
    if src in nodes_exp_backoff:
        node_history = nodes_exp_backoff[src]
        i = node_history['i']
        t_b = node_history['t_b']
    i += 1
    #NOTE: this is the error state, the associated packet should be dropped
    if i > K_MAX:
        nodes_exp_backoff.pop(src_name, None)
        return 0
    T_b = random.randint(0, math.pow(2, i) -1) * T_P
    nodes_exp_backoff[src] = {'i': i, 't_b': T_b}
    return T_b

# Returns true or false depending on if it's the right time to send.
def is_right_time(inputThread):
    logging.debug("[%s]: Thread:%s has a send time of: %s ticks" % \
            (is_right_time.__name__, inputThread, nodes_src_time_dict[inputThread]))
    logging.debug("[%s]: Thread:%s Current Tick: %s" % (is_right_time.__name__, inputThread,nodes_src_clk_dict[inputThread]))
    return (nodes_src_clk_dict[inputThread] >= nodes_src_time_dict[inputThread])


# return true when the node detects any signal from other sources
# medium is either busy or theres an collision
def is_medium_busy(from_index):
    for packet in link_queue:
        if packet.sender_index != from_index:
            if packet.is_detected(from_index, global_tick):
                return True
    return False
"""
Returns total sensing time depending on if the node has completed medium sensing
t = 0, the medium is busy
0 < t < SENSE_MEDIUM_TIME, sensing carrier and medium is idle for t ticks
t = SENSE_MEDIUM_TIME, complete carrier sensing
"""
def medium_sensing_time(src_name, src_idx):
    global nodes_src_sense_dict
    # the node is not done medium sensing
    if (nodes_src_sense_dict[src_name] <= SENSE_MEDIUM_TIME):
        if is_medium_busy(src_idx):
            nodes_src_sense_dict[src_name] = 0
        else:
            # increment sensing time
            nodes_src_sense_dict[src_name] += 1
    return nodes_src_sense_dict[src_name]

def transmit_worker():
    global nodes_src_clk_dict
    global nodes_src_time_dict
    global nodes_src_idle_dict
    global packet_dropped
    global packet_transmitted
    global packet_collided
    binary_backoff_time = 0
    src_name = threading.currentThread().getName()
    send_time = nodes_src_time_dict[src_name]
    src_idx = math.ceil(NODES_SRC_LIST.index(src_name) * 10 / (ETHERNET_SPEED*TICK_DURATION))
    newPacket = None
    current_tick = global_tick
    double_sensed = False
    while current_tick < TOTAL_TICKS:
        current_tick = global_tick

         # a tick passed by
        if (nodes_src_clk_dict[src_name] < current_tick):
            # update tick
            nodes_src_clk_dict[src_name] = current_tick

            if not is_right_time(src_name):
                logging.debug("[%s]: It's not the right time for me to transmit, so I'm gonna chill." % src_name)
                nodes_src_idle_dict[src_name] += 1
                continue

            # generate a new packet after getting an error in binary exponential backoff
            if (binary_backoff_time == 0):
                newPacket = Packet(src_name, src_idx, send_time)

            sensing_time = medium_sensing_time(src_name, src_idx)
            # medium is busy.. need to restart medium sensing
            if sensing_time == 0:
                # 1 persistance
                if P_PRAM == '1':
                    logging.debug("[%s]: Channel Busy, Restarting carrier sensing at next tick.." % (src_name))
                # non persistance
                elif P_PRAM == '2':
                    # update next transmit time with a random wait time
                    # wait time generated using last binary exponential backoff
                    if src_name in nodes_exp_backoff:
                        last_binary_exp = nodes_exp_backoff[src_name]['t_b']
                        nodes_src_time_dict[src_name] = random.random(0, last_binary_exp)
                    logging.debug("[%s]: Channel Busy, Restarting carrier sensing at tick %s.." %\
                            (src_name, nodes_src_time_dict[src_name]))
                # p persistance
                else:
                    # second time sensing
                    if double_sensed:
                        # binary exponential backoff
                        binary_backoff_time = binary_backoff(src_name)
                        if binary_backoff_time == 0:
                            # generate a new packet at the next gen time
                            # reset the all single packet related data
                            # the binary_backoff_time will generate a new packet at line 192
                            double_sensed = False
                            nodes_src_time_dict[src_name] = next_gen_time(current_tick)
                            packet_dropped += 1
                        else:
                            # will try to resend the packet after binary exponential backoff time
                            nodes_src_time_dict[src_name] = nodes_src_time_dict[src_name] + binary_backoff_time
                        logging.debug("[%s]: Channel Busy, Restarting carrier sensing at tick %s.." %\
                            (src_name, nodes_src_time_dict[src_name]))
                    # first time sensing
                    else:
                        logging.debug("[%s]: Channel Busy, Restarting carrier sensing at next tick.." % (src_name))

            # medium is idle at this tick
            elif sensing_time < SENSE_MEDIUM_TIME:
                # Nothing to do
                logging.info("[%s]: Medium Sensing for %s ticks" % (src_name, sensing_time))
            else:
                logging.info("[%s]: Medium Sensing completed, start to transmit" % (src_name))
                # node have transmitted packet with no collision
                if newPacket in link_queue:
                    # lets move on in life
                    if newPacket.is_fully_transmitted(current_tick):
                        logging.info("[%s] packet transmitted" % (src_name))
                        binary_backoff_time = 0
                        double_sensed = False
                        packet_transmitted += 1
                        nodes_exp_backoff.pop(src_name, None)
                        nodes_src_sense_dict[src_name] = 0
                        nodes_src_time_dict[src_name] = next_gen_time(current_tick)
                        logging.info("[%s]: next_gen at: %s" % (src_name, nodes_src_time_dict[src_name]))
                    # still in transmission.. performing collision detection
                    else:
                        # jamming signal detection
                        is_jammed = False
                        for packet in link_queue:
                            if (packet.jamming and (packet.sender != src_name)):
                                # abort current transmission
                                is_jammed = True
                                try:
                                    logging.info("[%s]: Abort Transmission" % (src_name))
                                    link_queue.remove(newpacket)
                                except Exception as e:
                                    logging.debug("[%s]: nothing to remove, safe. | ret_msg: %s" %\
                                            (src_name, e.message))
                                binary_backoff_time = 0
                                nodes_src_time_dict[src_name] = next_gen_time(current_tick)
                                logging.info("[%s]: Signal jammed" % (src_name))
                                logging.info("[%s]: Next_gen at: %s" % (src_name, nodes_src_time_dict[src_name]))
                            if not is_jammed:
                                # collision detected
                                collision_detected = is_medium_busy(src_idx)
                                if collision_detected:
                                    logging.info("[%s]: Collision Detected" % (src_name, current_tick))
                                    try:
                                        # abort current transmission
                                        logging.info("[%s]: Abort Transmission" % (src_name))
                                        link_queue.remove(newPacket)
                                    except Exception as e:
                                        logging.debug("[%s]: nothing to remove, safe. | ret_msg: %s" %\
                                            (src_name, e.message))
                                    # transmit jamming signal
                                    newPacket = Packet(src_name, src_idx, send_time, True)
                                    try:
                                        logging.info("[%s]: Transmit jamming signal" % (src_name, e.message))
                                        link_queue.append(newPacket)
                                    except Exception as e:
                                        logging.error("[%s]: Exception was raised! msg: %s" %\
                                                (src_name, e.message))
                                    finally:
                                        logging.info("[%s]: Start binary exponential backoff"% (src_name))
                                        packet_collided += 1
                                        # binary exponential backoff
                                        binary_backoff_time = binary_backoff(src_name)
                                        if binary_backoff_time == 0:
                                            packet_dropped += 1
                                        else:
                                            nodes_src_time_dict[src_name] = nodes_src_time_dict[src_name] + binary_backoff_time


                # packet is not transmittied
                else:
                    # special case for p persistant
                    if P_PRAM != '1' or P_REAM != '2':
                        prob = get_probability()
                        # defer packet
                        if prob >= float(P_PRAM):
                            double_sensed = True
                            nodes_src_time_dict[src_name] = next_gen_time(current_tick)

                    try:
                        link_queue.append(newPacket)
                    except Exception as e:
                        logging.error("[%s]: Exception was raised! msg: %s" % (src_name, e.message))
                    finally:
                        logging.info("[%s]: Packet Generated at %s" % (src_name, current_tick))

    logging.info("[%s]: Im done.. bai" % src_name)
    return

# The schedule basically calculates randomly generated
# times at which each node in the system would act as a transmitter.
# This assigns an initial order in which the nodes should be acting as transmitters
# each time a node tranmits, it request for the next_gen_time()
def scheduler(sender_thread_list, current_tick):
    global nodes_src_time_dict
    for node in sender_thread_list:
        nodes_src_time_dict[node] = next_gen_time(current_tick)
        logging.info("[%s]: next gen at: %s" % (node, nodes_src_time_dict[node]))

def nerdystats():
    logging.info("[%s]: packets transmitted: %s" % (nerdystats.__name__, packet_transmitted))
    logging.info("[%s]: packets collided   : %s" % (nerdystats.__name__, packet_collided))
    logging.info("[%s]: packets dropped    : %s" % (nerdystats.__name__, packet_dropped))

    for node in NODES_SRC_LIST:
        logging.debug("[%s]: Node #%s had idle time: %s ticks of fun time." %\
                (nerdystats.__name__, node, nodes_src_idle_dict[node]))

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
    global global_tick
    global_tick = 0
    while (global_tick < TOTAL_TICKS):
        # clock synchronization across all nodes
        all_updated = True
        for nodes in nodes_src_clk_dict:
            if nodes_src_clk_dict[nodes] < global_tick:
                all_updated = False

        if all_updated:
            global_tick += 1
            if (global_tick % 100 == 0):
                logging.info("[%s]: current global tick at: %s" % (tickTock.__name__, global_tick))
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
    # total amount of ticks to run
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
        global NODES_SRC_LIST
        NODES_SRC_LIST.append(t.getName())
        global nodes_src_clk_dict
        nodes_src_clk_dict[t.getName()] = 0
        global nodes_src_time_dict
        nodes_src_time_dict[t.getName()] = 0
        global nodes_src_idle_dict
        nodes_src_idle_dict[t.getName()] = 0
        global nodes_src_sense_dict
        nodes_src_sense_dict[t.getName()] = 0


    # Call the scheduler right now to determine times to send.
    scheduler(NODES_SRC_LIST, 0)

    # Let it rip.
    main(argsDict)

if __name__ == '__main__':
    init()
