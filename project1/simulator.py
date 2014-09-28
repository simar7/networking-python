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
import math

# TODO: I think this is okay but I'll ask the TA and the prof.
# worst case we will end up writing our own clock.
def tickTock(tickDuration, TOTAL_TICKS, update_tick, lock):
    for tick in xrange(0, int(TOTAL_TICKS)):
        print "[%s]: Current tick %s" % (tickTock.__name__, tick)
        with lock:
            update_tick.value = tick
        time.sleep(float(tickDuration))

# TODO: refactor the constants with the global values
def next_generate_time(DISTRIBUTION, LAMBDA, TICK_DURATION, current_tick):
    if DISTRIBUTION == "M":
        gen_number = random.random()
        next_gen_time = (-1/int(LAMBDA))*math.log(1-gen_number)
        next_gen_tick = math.ceil(next_gen_time/float(TICK_DURATION))
        return (next_gen_tick + current_tick)
    else:
        raise Exception("Unknow distriution")

def transmitter(ARRIVAL_DIST, LAMBDA, TICK_DURATION, TOTAL_TICKS, current_tick, packet_queue):
    print "[%s]: queue size: %s" % (transmitter.__name__, packet_queue.qsize())
    next_generation = next_generate_time(ARRIVAL_DIST, LAMBDA, TICK_DURATION, current_tick.value)
    # calculate when to create new packet
    while (current_tick.value < int(TOTAL_TICKS)-1):
        # in case the tick is changed during the calculation
	tmp_tick = current_tick.value
    	if (tmp_tick >= next_generation):
            # TODO: create a packet object to keep track of data
            packet_data = "packet"
            if packet_queue.full():
                print "[%s]: Failed to transmit: %s" % (transmitter.__name__, packet_data)
            else:
                print "[%s]: Transmit: %s" % (transmitter.__name__, packet_data)
                packet_queue.put(packet_data)
            next_generation = next_generate_time(ARRIVAL_DIST, LAMBDA, TICK_DURATION, tmp_tick)
            print "[%s] next_generation_time: %s" % (transmitter.__name__, next_generation)

def receiver(TICK_DURATION, TOTAL_TICKS, SERVICE_TIME, PACKET_LENGTH, current_tick, packet_queue):
    next_service_time = 0
    service_time = int(PACKET_LENGTH)/int(SERVICE_TIME)
    service_ticks = math.ceil(service_time/int(TICK_DURATION))
    print "[%s]: service interval: %s" % (receiver.__name__, service_ticks)
    # TODO: recieve packet at the correct tick, this is written to test the transmitter
    while (current_tick.value < int(TOTAL_TICKS)-1):
	tmp_tick = current_tick.value
    	if (tmp_tick >= next_service_time):
            print "[%s] next_service_time: %s" % (receiver.__name__, next_service_time)
            if packet_queue.empty():
                print "[%s] Server is idle" % (receiver.__name__)
                next_service_time += 1
            else:
                print "[%s] Serve packet: %s" % (receiver.__name__, packet_queue.get())
                next_service_time += service_ticks
            print "[%s] next_service_time: %s" % (receiver.__name__, next_service_time)

def main(argv):
    print "Program is starting..."

def init():
    parser = argparse.ArgumentParser(description = \
            "M/D/1 and M/D/1/K Queue Simulation")
    # distribution of arrive time
    parser.add_argument('--arrival', action="store", default="M")
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
    # service time for each packet per second
    parser.add_argument('-C', action="store", default="500")

    # args is a type dict.
    argsDict = vars(parser.parse_args())

    # lock for timer
    lock = multiprocessing.Lock()
    # shared objects between processes
    # create a process queue
    if (argsDict['size'] == "inf"):
        packet_queue = multiprocessing.Queue()
    else:
        packet_queue = multiprocessing.Queue(int(argsDict['size']))

    # a shared memory for the tick
    # TODO: I am not sure if this is the best way to do it
    current_tick = multiprocessing.Value('i', 0)

    # Init our processes.
    # TODO: Find a better way of doing this
    tickTockPID = multiprocessing.Process(target=tickTock,
      args=(argsDict['tickLen'], argsDict['numOfTicks'], current_tick, lock))
    transmitterPID = multiprocessing.Process(target=transmitter,
      args=(argsDict['arrival'], argsDict['lambda'], argsDict['tickLen'], argsDict['numOfTicks'],
            current_tick, packet_queue))
    receiverPID = multiprocessing.Process(target=receiver,
      args=(argsDict['tickLen'], argsDict['numOfTicks'], argsDict['C'], argsDict['L'], current_tick, packet_queue))

    # Spawn our processes.
    tickTockPID.start()
    transmitterPID.start()
    receiverPID.start()

    # Let it rip.
    main(argsDict)

if __name__ == '__main__':
  init()
