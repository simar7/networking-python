#!/usr/bin/python
'''
    ECE 358: Computer Networks
    Project: CSMA/CD protocols
    Author:  Simarpreet Singh (s244sing@uwaterloo.ca)
             Louisa Chong (l5chong@uwaterloo.ca)

'''
import sys
import random
import subprocess

testList = []
packetPerSecList = []
numberOfNodesList = []

lan_speed = 10000000
pkt_len_in_bits = 12000
p_pram = [1, 2, 3]
ticklen = 1e-2
totalticks = 1000
whatWeNeed = None

wittyErrorMsgs = ["You're a bad tester, go home.", \
                  "Please handle with care, stuff borked", \
                  "I'm sorry master, this didn't work out", \
                  "@#$*@#$ @#$( @#*$ @#$(&^^ @**$#@", \
                  "110101 100100 010101 10010101 100100101 10010"]

def makeTests():
    for nodeCount in numberOfNodesList:
        for avgPackets in packetPerSecList:
            global testList
            testList.append('./simulator.py -N %s -A %s -W %s -L %s -P %s --tickLen %s -T %s --calc %s' %\
                    (nodeCount, avgPackets, lan_speed, pkt_len_in_bits, str(p_pram[0]), ticklen, totalticks, whatWeNeed))

def makeTests_Q5(p_list, nodeCount):
    for pers in p_list:
        for avgPackets in packetPerSecList:
            global testList
            testList.append('./simulator.py -N %s -A %s -W %s -L %s -P %s --tickLen %s -T %s --calc %s' %\
                    (nodeCount, avgPackets, lan_speed, pkt_len_in_bits, pers, ticklen, totalticks, whatWeNeed))

def runTests():
    print "[%s]: Brace yourself, running tests now..." % (runTests.__name__)
    try:
        for test in testList:
            print "[%s]: Currently running: %s" % (runTests.__name__, test)
            process = subprocess.Popen(test, shell=True)
            process.wait()
    except Exception as e:
        print "Computer> %s \nComputer>  ret_msg: %s | ret_code: %s" % \
                (wittyErrorMsgs[random.randint(0, len(wittyErrorMsgs)-1)], e.message, process.returncode)

def main(args):
    try:
        if args[1] == 'sanity':
            global packetPerSecList
            packetPerSecList.append(5)
            global numberOfNodesList
            numberOfNodesList.append(5)
            global whatWeNeed
            whatWeNeed = 'throughput'
            global testlist
            testList.append('./simulator.py -N %s -A %s -W %s -L %s -P %s --tickLen %s -T %s --calc %s' %\
                    (numberOfNodesList[0], packetPerSecList[0], lan_speed, \
                    pkt_len_in_bits, p_pram[2], ticklen, totalticks, whatWeNeed))

        elif args[1] == 'q1':
            for nodeCount in xrange(20, 120, 20):
                numberOfNodesList.append(nodeCount)
            for avgPackets in [5, 6, 7]:
                packetPerSecList.append(avgPackets)
            whatWeNeed = 'throughput'
            makeTests()

        elif args[1] == 'q2':
            for nodeCount in xrange(20, 50, 10):
                numberOfNodesList.append(nodeCount)
            for avgPackets in [4, 24, 4]:
                packetPerSecList.append(avgPackets)
            whatWeNeed = 'throughput'
            makeTests()

        elif args[1] == 'q3':
            for nodeCount in xrange(20, 120, 20):
                numberOfNodesList.append(nodeCount)
            for avgPackets in [5, 6, 7]:
                packetPerSecList.append(avgPackets)
            whatWeNeed = 'avgDelay'
            makeTests()

        elif args[1] == 'q4':
            for nodeCount in xrange(20, 50, 10):
                numberOfNodesList.append(nodeCount)
            for avgPackets in [4, 24, 4]:
                packetPerSecList.append(avgPackets)
            whatWeNeed = 'avgDelay'
            makeTests()

        elif args[1] == 'q5':
            persistence_list = [0.01, 0.1, 0.3, 0.6, 1]
            servers = 30
            packetPerSecList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            whatWeNeed = 'both'
            makeTests_Q5(persistence_list, servers)

        else:
            raise Exception("Please enter a valid question to solve for.")

        # Decide your fate.
        runTests()

    except Exception as e:
        print "Computer> %s \nComputer> ret_msg: %s" % \
                (wittyErrorMsgs[random.randint(0, len(wittyErrorMsgs)-1)], e.message)

if __name__ == '__main__':
    main(sys.argv)
