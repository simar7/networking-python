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
def tickTock(tickDuration, TOTAL_TICKS, update_tick):
    for tick in xrange(0, int(TOTAL_TICKS)):
        print "[%s]: Sleeping for %s seconds." % (tickTock.__name__, tickDuration)
        update_tick.value = tick
        time.sleep(float(tickDuration))

def next_generate_time(DISTRIBUTION, LAMBDA, TICK_DURATION, current_tick):
    # TODO: add check for the distribution required for the tx
    if DISTRIBUTION == "M":
        gen_number = random.random()
        next_gen_time = (-1/int(LAMBDA))*math.log(1-gen_number)
        next_gen_tick = math.ceil(next_gen_time/float(TICK_DURATION))
        return (next_gen_tick + current_tick)
    else:
        raise Exception("Unknow distriution")


def transmitter(ARRIVAL_DIST, LAMBDA, TICK_DURATION, TOTAL_TICKS, current_tick, packet_queue):
    next_generation = next_generate_time(ARRIVAL_DIST, LAMBDA, TICK_DURATION, current_tick.value)
    # calculate when to create new packet
    while (current_tick.value < int(TOTAL_TICKS)-1):
        # in case the tick is changed during the calculation
	tmp_tick = current_tick.value
    	if (tmp_tick >= next_generation):
            print "[%s]: Transmitting.." % (transmitter.__name__)
            packet_queue.put("packet")
            next_generation = next_generate_time(ARRIVAL_DIST, LAMBDA, TICK_DURATION, tmp_tick)

def receiver(packetRxData, TOTAL_TICKS, current_tick, packet_queue):
    # TODO: recieve packet at the correct tick, this is written to test the transmitter
    while (current_tick.value < int(TOTAL_TICKS)-1):
        if not packet_queue.empty():
            print "[%s] Packet_received: %s" % (receiver.__name__, packet_queue.get())

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

    # args is a type dict.
    argsDict = vars(parser.parse_args())

    # shared objects between processes
    # create a process queue
    packet_queue = multiprocessing.Queue()
    # a shared memory for the tick
    # TODO: I am not sure if this is the best way to do it
    current_tick = multiprocessing.Value('i', 0)

    # Init our processes.
    # TODO: Find a better way of doing this
    tickTockPID = multiprocessing.Process(target=tickTock,
      args=(argsDict['tickLen'], argsDict['numOfTicks'], current_tick))
    transmitterPID = multiprocessing.Process(target=transmitter,
      args=(argsDict['arrival'], argsDict['lambda'], argsDict['tickLen'], argsDict['numOfTicks'],
            current_tick, packet_queue))
    receiverPID = multiprocessing.Process(target=receiver,
      args=('r', argsDict['numOfTicks'], current_tick, packet_queue))

    # Spawn our processes.
    tickTockPID.start()
    transmitterPID.start()
    receiverPID.start()

    # Let it rip.
    main(argsDict)

if __name__ == '__main__':
  init()
