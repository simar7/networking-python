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
global_tick       = 0

# BEB Params
K_MAX = 10
T_P = 0

NODES_SRC_LIST        = []
NODES_SRC_INDEX       = {}
nodes_src_time_dict   = {} # key:value <=> src_node_thread:tx_time
nodes_src_idle_dict   = {} # key:value <=> src_node_thread:idle_time
nodes_src_sense_dict  = {} # key:value <=> src_node_thread:medium sensing time
nodes_src_buffer_dict = {} # key:value <=> src_node_thread:buffer dict
nodes_src_send_time   = {} # key:value <=> node:send_time
packet_in_transit     = {} # key:value <=> node:packet in tansit
nodes_send_time       = {}
nodes_beb_count       = {}
nodes_last_binary_exp = {}
nodes_double_sensed   = {}
nodes_exp_backoff     = {} # key:value <=> node:{i: index, Tb : wait_time}


sender_threads       = []
link_queue           = []
global_tick          = 0

# Data Collection
packet_dropped      = 0
packet_transmitted  = 0
packet_collided     = 0
packet_defered      = 0
CALC                = None
throughput          = 0
total_delay         = 0.0
avgDelay            = 0.0
"""
Useful Object
"""

class Packet:
    def __init__(self, sender, sender_index, gen_time, jamming = False):
        self.data = "fun"
        self.jamming = jamming
        self.sender = sender
        self.sender_index = sender_index
        self.gen_time = gen_time
        self.send_time = None

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
        return (((max_index >= from_index) and (from_index >= self.sender_index))
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
            if current_tick % D_TRANS == 0:
                logging.debug("[%s]: current_tick: %s | send_time: %s | D_TRANS: %s" % ("is_fully_transmitted", current_tick, self.send_time, D_TRANS))
                return ((current_tick - self.send_time) >= D_TRANS)

"""
Helper Functions
"""

def get_probability():
    return random.random()

def dequeue_helper():
    for packet in link_queue:
        packet_trans_dist = max(packet.sender_index, D_TOTAL_PROP - packet.sender_index)
        # jamming packet take 48 bit time to transmit + propagation delay
        if packet.jamming:
            if (global_tick > packet.send_time + packet_trans_dist + JAMMING_TIME):
                try:
                    link_queue.remove(packet)
                    logging.debug("[%s] Jamming signal from sender %s at time %s" %\
                        (dequeue_helper.__name__, packet.sender, global_tick))
                except Exception as e:
                    logging.debug("[%s]: nothing to remove, safe. | ret_msg: %s" %\
                        (dequeue_helper.__name__, e.message))
        else:
            if (global_tick >= packet.send_time + packet_trans_dist + D_TRANS):
                try:
                    link_queue.remove(packet)
                    logging.debug("[%s] Packet from sender %s at time %s" %\
                            (dequeue_helper.__name__, packet.sender, global_tick))
                    global total_delay
                    total_delay += (packet.send_time - packet.gen_time)
                except Exception as e:
                    logging.debug("[%s]: nothing to remove, safe. | ret_msg: %s" %\
                        (dequeue_helper.__name__, e.message))

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
        nodes_exp_backoff.pop(src, None)
        return -1
    T_b = random.randint(0, math.pow(2, i) -1) * T_P
    nodes_exp_backoff[src] = {'i': i, 't_b': T_b}
    return T_b

# Returns true or false depending on if it's the right time to send.
def is_right_time(node):
    logging.debug("[%s]: Node:%s has a generationg time of: %s ticks" % \
            (is_right_time.__name__, node, nodes_src_time_dict[node]))
    return (global_tick >= nodes_src_time_dict[node])


# return true when the node detects any signal from other sources
# medium is either busy or theres an collision
def is_medium_busy(src_name,from_index):
    for packet in link_queue:
        if packet.sender != src_name:
            if packet.is_detected(from_index, global_tick):
                logging.debug("[%s] Packet from %s detected: %s" %\
                    (is_medium_busy.__name__, packet.sender, packet.is_detected(from_index, global_tick)))
                return True
    return False

"""
Returns total sensing time depending on if the node has completed medium sensing
t = 0, the medium is busy
0 < t < SENSE_MEDIUM_TIME, sensing carrier and medium is idle for t ticks
t = SENSE_MEDIUM_TIME, complete carrier sensing
"""
def medium_sensing_time(current_tick, src_name, src_idx):
    global nodes_src_sense_dict
    # the node is not done medium sensing
    if (nodes_src_sense_dict[src_name] <= SENSE_MEDIUM_TIME):

        if is_medium_busy(src_name, src_idx):
            logging.debug("[%s]: Sensed busy medium at: %s" % (src_name, current_tick))
            nodes_src_sense_dict[src_name] = 0
        else:
            # increment sensing time
            logging.debug("[%s]: Medium is not busy at: %s" % (src_name, current_tick))
            nodes_src_sense_dict[src_name] += 1
    return nodes_src_sense_dict[src_name]

def node(node):
    global nodes_src_clk_dict
    global nodes_src_time_dict
    global nodes_src_idle_dict
    global packet_dropped
    global packet_transmitted
    global packet_collided
    global nodes_src_buffer_dict
    global packet_in_transit
    global nodes_send_time
    global nodes_beb_count
    global nodes_last_binary_exp
    global nodes_double_sense

    if is_right_time(node):
        # find next generation time
        nodes_src_time_dict[node] = next_gen_time(global_tick)
        tmp_packet = Packet(node, NODES_SRC_INDEX[node], global_tick)
        nodes_src_buffer_dict[node].append(tmp_packet)
        logging.debug("[%s] new packet generated at tick %s" % (node, global_tick))
    else:
        logging.debug("[%s]: It's not the right time for me to generate, so I'm gonna chill." % node)
        nodes_src_idle_dict[node] += 1

    # get a new packet after getting an error in binary exponential backoff
    if (nodes_beb_count[node] == -1):
        # get a new packet from the queue
        if len(nodes_src_buffer_dict[node]) > 0:
            packet_in_transit[node] = nodes_src_buffer_dict[node].pop(0)
            # unset the error flag
            nodes_beb_count[node] = 0
            nodes_send_time[node] = packet_in_transit[node].gen_time
            logging.debug("[%s] packet generated at tick %s is now ready to send" % (node, packet_in_transit[node].gen_time))
        else:
            return

    # when in binary exponential back off wait till time has passed
    if nodes_send_time[node] > global_tick:
        logging.debug("[%s] The next sent time is at tick %s" % (node, nodes_send_time[node]))
        return

    if packet_in_transit[node] in link_queue:
        # lets move on in life
        ret = packet_in_transit[node].is_fully_transmitted(global_tick)
        if ret:
            logging.debug("[%s]: ret = %s" % (node, ret))
            if packet_in_transit[node].jamming:
                # binary exponential backoff
                logging.debug("[%s]: jamming signal finished" % (node))
                nodes_beb_count[node] = binary_backoff(node)
                if nodes_beb_count[node] == -1:
                    packet_dropped += 1
                else:
                    logging.debug("[%s]: Start binary exponential backoff at tick %s"% (node, global_tick))
                    nodes_send_time[node] = global_tick + nodes_beb_count[node]
            else:
                logging.debug("[%s]: packet finished at tick %s" % (node, global_tick))
                packet_transmitted += 1
            nodes_beb_count[node] = -1
            nodes_double_sensed[node] = False
            if node in nodes_exp_backoff:
                binary_exp = nodes_exp_backoff.pop(node)
                nodes_last_binary_exp[node] = binary_exp['t_b']
            nodes_src_sense_dict[node] = 0
        # still in transmission.. performing collision detection
        else:
            logging.debug("[%s]: still in tx" % node)
            # jamming signal detection
            is_jammed = False
            for packet in link_queue:
                if (packet.jamming and (packet.sender != node)):
                    # abort current transmission
                    is_jammed = True
                    try:
                        link_queue.remove(packet_in_transit[node])
                        logging.debug("[%s]: Abort Transmission at tick %s" %\
                                (node, global_tick))
                    except Exception as e:
                        logging.debug("[%s]: Nothing to remove, safe. | ret_msg: %s" %\
                                (node, e.message))
                    finally:
                        packet_collided += 1
                        logging.debug("[%s]: Signal jammed at tick %s" % (node, global_tick))
                        # binary exponentail backoff after seeing jamming signal
                        nodes_beb_count[node] = binary_backoff(node)
                        if nodes_beb_count[node] == -1:
                            logging.debug("[%s]: Error in binary exponential backoff " % (node))
                            packet_dropped += 1
                        else:
                            logging.debug("[%s]: Start binary exponential backoff" % (node))
                            nodes_send_time[node] = global_tick + nodes_beb_count[node]
                        nodes_beb_count[node] = -1
                        nodes_src_sense_dict[node] = 0
                        logging.debug("[%s]: Jamming signal caused next_gen at: %s" %\
                                (node,nodes_src_time_dict[node]))
            if not is_jammed:
                # collision detected
                collision_detected = is_medium_busy(node, NODES_SRC_INDEX[node])
                if collision_detected:
                    logging.debug("[%s]: Collision Detected at tick %s" %\
                            (node, global_tick))
                    try:
                        nodes_src_sense_dict[node] = 0
                        link_queue.remove(packet_in_transit[node])
                        # abort current transmission
                        logging.debug("[%s]: Abort Transmission at tick %s" %\
                                (node, global_tick))
                    except Exception as e:
                        logging.debug("[%s]: Nothing to remove, safe. | ret_msg: %s" %\
                            (node, e.message))
                    # put the current packet back to queue to retransmit
                    nodes_src_buffer_dict[node].insert(0, packet_in_transit[node])
                    # transmit jamming signal
                    packet_in_transit[node] = Packet(node, NODES_SRC_INDEX[node], global_tick, True)
                    packet_in_transit[node].send_time= global_tick
                    try:
                        link_queue.append(packet_in_transit[node])
                        logging.debug("[%s]: Transmit jamming signal at tick %s" %\
                                (node, global_tick))
                    except Exception as e:
                        logging.error("[%s]: Exception was raised! msg: %s" %\
                                (node, e.message))
                    finally:
                        packet_collided += 1

    else:
        sensing_time = medium_sensing_time(global_tick, node, NODES_SRC_INDEX[node])
        # medium is busy.. need to restart medium sensing
        if sensing_time == 0:
            # 1 persistance
            if P_PRAM == '1':
                logging.debug("[%s]: Channel Busy, Restarting carrier sensing at next tick.." % (node))
            # non persistance
            elif P_PRAM == '2':
                # update next transmit time with a random wait time
                # wait time generated using last binary exponential backoff
                if node in nodes_exp_backoff:
                    nodes_send_time[node] = global_tick + random.uniform(0, nodes_last_binary_exp[node])

                logging.debug("[%s]: Channel Busy, Restarting carrier sensing at tick %s.." %\
                        (node, nodes_src_time_dict[node]))
            # p persistance
            else:
                # second time sensing
                if nodes_double_sensed[node]:
                    # binary exponential backoff
                    nodes_beb_count[node] = binary_backoff(node)
                    if nodes_beb_count[node] == -1:
                        # generate a new packet at the next gen time
                        # reset the all single packet related data
                        # the nodes_beb_count[node] will generate a new packet at line 192
                        nodes_double_sensed[node] = False
                        packet_dropped += 1
                    else:
                        # will try to resend the packet after binary exponential backoff time
                        nodes_send_time[node] = global_tick + nodes_beb_count[node]
                    logging.debug("[%s]: Channel Busy, Restarting carrier sensing at tick %s.." %\
                        (node, nodes_src_time_dict[node]))
                # first time sensing
                else:
                    logging.debug("[%s]: Channel Busy, Restarting carrier sensing at next tick.." % (node))

        # medium is idle at this tick
        elif sensing_time < SENSE_MEDIUM_TIME:
            # Nothing to do
            logging.debug("[%s]: Medium Sensing for %s ticks at tick %s" %\
                    (node, sensing_time, global_tick))
        else:
            # special case for p persistant
            if P_PRAM != '1' and P_PRAM != '2':
                prob = get_probability()
                # defer packet
                if prob >= float(P_PRAM):
                    nodes_double_sensed[node] = True
                    global packet_defered
                    packet_defered += 1
                    # put the current packet back to queue to retransmit
                    nodes_src_buffer_dict[node].insert(0, packet_in_transit[node])
                    nodes_beb_count[node] = -1
                    packet_in_transit[node] = None

            # transmit packet when packet is not deferred
            if packet_in_transit[node] != None:
                try:
                    logging.debug("[%s]: Medium Sensing completed, start to transmit at tick %s" %\
                            (node, global_tick))
                    packet_in_transit[node].send_time = global_tick
                    link_queue.append(packet_in_transit[node])
                except Exception as e:
                    logging.error("[%s]: Exception was raised! msg: %s" % (node, e.message))
                finally:
                    logging.debug("[%s]: Packet start txing at tick %s" % (node, global_tick))


# The schedule basically calculates randomly generated
# times at which each node in the system would act as a transmitter.
# This assigns an initial order in which the nodes should be acting as transmitters
# each time a node tranmits, it request for the next_gen_time()
# also find when the first packet is transmitted
def scheduler(sender_thread_list, current_tick):
    min_time = TOTAL_TICKS

    global nodes_src_time_dict
    for node in sender_thread_list:
        gen_time = next_gen_time(current_tick)
        nodes_src_time_dict[node] = gen_time
        min_time = min(min_time, gen_time)
        logging.debug("[%s]: next gen at: %s" % (node, nodes_src_time_dict[node]))

    # skip the initial wait to tranmit the first packet
    global START_TICK
    START_TICK = min_time - 10


def nerdystats():
    logging.info("[%s]: packets transmitted: %s" % (nerdystats.__name__, packet_transmitted))
    logging.info("[%s]: packets collided   : %s" % (nerdystats.__name__, packet_collided))
    logging.info("[%s]: packets dropped    : %s" % (nerdystats.__name__, packet_dropped))
    logging.info("[%s]: packets defered    : %s" % (nerdystats.__name__, packet_defered))
    logging.info("[%s]: len of link_queue  : %s" % (nerdystats.__name__, len(link_queue)))

    global throughput
    throughput =  packet_transmitted / TOTAL_TIME

    for node in NODES_SRC_LIST:
        logging.debug("[%s]: Node #%s had idle time: %s ticks of fun time." %\
                (nerdystats.__name__, node, nodes_src_idle_dict[node]))

    global avgDelay
    avgDelay = (total_delay*TICK_DURATION) / packet_transmitted

    if CALC == 'throughput':
        logging.info("[%s]:  Throughput    : %s" % (nerdystats.__name__, throughput))
        logging.info("[%s]: Average Delay : %s" % (nerdystats.__name__, avgDelay))
    if CALC == 'avgDelay':
        logging.info("[%s]:  Average Delay : %s" % (nerdystats.__name__, avgDelay))
        logging.info("[%s]: Throughput    : %s" % (nerdystats.__name__, throughput))
    if CALC == 'both':
        logging.info("[%s]: Average Delay : %s(sec)" % (nerdystats.__name__, avgDelay))
        logging.info("[%s]: Throughput    : %s(pkt/sec)" % (nerdystats.__name__, throughput))
    else:
        logging.error("[%s]: Invalid Calculation parameter" % (nerdystats.__name__))

def tickTock():
    for i in nodes_src_idle_dict:
        nodes_src_idle_dict[i] += START_TICK

    for i in xrange(START_TICK, TOTAL_TICKS):
        global global_tick
        global_tick = i
        if i % 1000 == 0:
            logging.debug("[%s]: current global tick at: %s \n" % (tickTock.__name__, global_tick))
        for j in xrange(0, SERVERS):
            node(j)
        dequeue_helper()

def main(argv):
    print "Program is starting..."
    # Start all the threads.
    tickTock()
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
    logging.debug("[%s]: Transmission Delay: %s" % (init.__name__, D_TRANS))
    # the total ticks it take for a packet to be propagated
    # from the first node to the last node
    global D_TOTAL_PROP
    D_TOTAL_PROP      = math.ceil((10*(SERVERS-1)) / (ETHERNET_SPEED*TICK_DURATION))
    logging.debug("[%s]: Total Propagation Delay: %s" % (init.__name__, D_TOTAL_PROP))
    # 512 bit time in ticks
    global T_P
    T_P               = math.ceil(512/(LAN_SPEED*TICK_DURATION))
    global MAX_LINK_SIZE
    MAX_LINK_SIZE     = LAN_SPEED * 8
    # convert 96 bit time to ticks
    global SENSE_MEDIUM_TIME
    SENSE_MEDIUM_TIME = math.ceil(96/(LAN_SPEED*TICK_DURATION))
    logging.debug("[%s]: Sense Medium Time: %s" % (init.__name__, SENSE_MEDIUM_TIME))
    # convert 48 bit time to ticks
    global JAMMING_TIME
    JAMMING_TIME = math.ceil(48/(LAN_SPEED*TICK_DURATION))
    logging.debug("[%s]: Jamming Time: %s" % (init.__name__, JAMMING_TIME))

    '''
    initiate date for the nodes
    '''
    # Each node is a possible sender and is a thread.
    for i in xrange(0, SERVERS):
        global NODES_SRC_LIST
        NODES_SRC_LIST.append(i)
        global NODES_SRC_INDEX
        NODES_SRC_INDEX[i] = math.ceil((i * 10) / (ETHERNET_SPEED*TICK_DURATION))
        global nodes_src_time_dict
        nodes_src_time_dict[i] = 0
        global nodes_src_idle_dict
        nodes_src_idle_dict[i] = 0
        global nodes_src_sense_dict
        nodes_src_sense_dict[i] = 0
        global nodes_src_buffer_dict
        nodes_src_buffer_dict[i] = []
        global packet_in_transit
        packet_in_transit[i] = None
        global nodes_send_time
        nodes_send_time[i] = nodes_src_time_dict[i]
        global nodes_beb_count
        nodes_beb_count[i] = -1
        global nodes_last_binary_exp
        nodes_last_binary_exp[i] = 0
        global nodes_double_sense
        nodes_double_sensed[i] = False


    # Call the scheduler right now to determine times to send.
    scheduler(NODES_SRC_LIST, 0)

    # Let it rip.
    main(argsDict)

if __name__ == '__main__':
    init()
