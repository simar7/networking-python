#!/usr/bin/python
'''
    ECE 358: Computer Networks
    Project: CSMA/CD protocols
    Author:  Simarpreet Singh (s244sing@uwaterloo.ca)
             Louisa Chong (l5chong@uwaterloo.ca)

'''
import sys
import datetime, time
from time import strftime
import random
import subprocess

testList = []
packetPerSecList = []
numberOfNodesList = []

lan_speed = 1000000
pkt_len_in_bits = 12000
# 1 = 1-Per; 2 = No-per; p(float) = p(float)-per
p_pram_sanity = [1]
p_pram = [2, 0.01, 0.1, 0.5, 0.6, 0.9, 1]
p_pram_q5 = [0.01, 0.1, 0.3, 0.6, 1]
ticklen = 1e-6
totalticks = int(1e7)
whatWeNeed = None

wittyErrorMsgs = ["You're a bad tester, go home.", \
                  "Please handle with care, stuff borked", \
                  "I think the prof cares less about this project that you do", \
                  "I'm sorry master, this didn't work out", \
                  "@#$*@#$ @#$( @#*$ @#$(&^^ @**$#@", \
                  "Well.. what are you waiting for, fix this shit cuz it ain't workin.", \
                  "DAT AP tho..", \
                  "110101 100100 010101 10010101 100100101 10010"]

def makeTests():
    for nodeCount in numberOfNodesList:
        for avgPackets in packetPerSecList:
            for perElem in xrange(0, len(p_pram)):
                global testList
                testList.append('./simulator.py -N %s -A %s -W %s -L %s -P %s --tickLen %s -T %s --calc %s' %\
                        (nodeCount, avgPackets, lan_speed, pkt_len_in_bits, str(p_pram[perElem]), ticklen, totalticks, whatWeNeed))

def makeTests_Q5(nodeCount):
    for avgPackets in packetPerSecList:
        for perElem in xrange(0, len(p_pram_q5)):
            global testList
            testList.append('./simulator.py -N %s -A %s -W %s -L %s -P %s --tickLen %s -T %s --calc %s' %\
                    (nodeCount, avgPackets, lan_speed, pkt_len_in_bits, p_pram_q5[perElem], ticklen, totalticks, whatWeNeed))

def runTests():
    print "[%s]: Brace yourself, running tests now..." % (runTests.__name__)
    try:
        cur_sys_time = strftime("%H:%M:%S:%MS", time.localtime())
        with open("%s.log" % cur_sys_time, "a+") as logFile:
            for test in testList:
                print >>logFile, ("[%s]: Currently running: %s\n" % (runTests.__name__, test))
                logFile.flush()
                process = subprocess.Popen(test, shell=True, stdout=logFile, stderr=logFile)
                process.wait()
                logFile.flush()
    except Exception as e:
        print "Computer> %s \nComputer>  ret_msg: %s | ret_code: %s" % \
                (wittyErrorMsgs[random.randint(0, len(wittyErrorMsgs)-1)], e.message, process.returncode)

def main(args):
    try:
        if args[1] == 'sanity':
            global packetPerSecList
            # NOTE: Increasing packet per sec for testing collision
            packetPerSecList.append(100)
            global numberOfNodesList
            numberOfNodesList.append(3)
            global whatWeNeed
            whatWeNeed = 'throughput'
            global testlist
            testList.append('./simulator.py -N %s -A %s -W %s -L %s -P %s --tickLen %s -T %s --calc %s' %\
                    (numberOfNodesList[0], packetPerSecList[0], lan_speed, \
                    pkt_len_in_bits, p_pram_sanity[0], ticklen, totalticks, whatWeNeed))

        elif args[1] == 'q1':
            for nodeCount in xrange(20, 120, 20):
                numberOfNodesList.append(nodeCount)
            for avgPackets in [5, 6, 7]:
                packetPerSecList.append(avgPackets)
            whatWeNeed = 'both'
            makeTests()

        elif args[1] == 'q2':
            for nodeCount in xrange(20, 50, 10):
                numberOfNodesList.append(nodeCount)
            for avgPackets in [4, 24, 4]:
                packetPerSecList.append(avgPackets)
            whatWeNeed = 'both'
            makeTests()

        elif args[1] == 'q3':
            for nodeCount in xrange(20, 120, 20):
                numberOfNodesList.append(nodeCount)
            for avgPackets in [5, 6, 7]:
                packetPerSecList.append(avgPackets)
            whatWeNeed = 'both'
            makeTests()

        elif args[1] == 'q4':
            for nodeCount in xrange(20, 50, 10):
                numberOfNodesList.append(nodeCount)
            for avgPackets in [4, 24, 4]:
                packetPerSecList.append(avgPackets)
            whatWeNeed = 'both'
            makeTests()

        elif args[1] == 'q5':
            servers = 30
            packetPerSecList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            whatWeNeed = 'both'
            makeTests_Q5(servers)

        else:
            raise Exception("Please enter a valid question to solve for.")

        # Decide your fate.
        runTests()

    except Exception as e:
        print "Computer> %s \nComputer> ret_msg: %s" % \
                (wittyErrorMsgs[random.randint(0, len(wittyErrorMsgs)-1)], e.message)

if __name__ == '__main__':
    main(sys.argv)
