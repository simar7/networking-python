#!/usr/bin/python
'''
     ECE 358: Computer Networks
     Project: M/D/1 and M/D/1/K Queue Simulation
     Author:  Simarpreet Singh (s244sing@uwaterloo.ca)
              Louisa Chong (l5chong@uwaterloo.ca)
'''
import sys
import subprocess

def main(args):
    if args[1] == 'Q2':
        test = './simulator.py --generation M --tickLen 0.0000001 --numOfTicks 100000 --service D --lambda 100 -L 2000 -C 1000000 --size inf'
        times = 1
    elif args[1] == 'Q3':
        test = ''

    try:
        for repeat in xrange(0, times):
            process = subprocess.Popen(test, shell=True)
    except Exception as e:
        print "Nasty stuff took place... ~eery silence~: %s \n \
               Process returned = %s" % e.message, process.returncode

if __name__ == '__main__':
    main(sys.argv)
