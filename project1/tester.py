#!/usr/bin/python
'''
     ECE 358: Computer Networks
     Project: M/D/1 and M/D/1/K Queue Simulation
     Author:  Simarpreet Singh (s244sing@uwaterloo.ca)
              Louisa Chong (l5chong@uwaterloo.ca)
'''
import sys
import numpy
import subprocess

rhoValues = 0
testList = []
times = 1

# TODO: We can do another argparse here but whatever.
def main(args):
    if args[1] == 'sanity':
        times = int(args[2])
        testList.append('./simulator.py --generation M --tickLen 0.0000001 --numOfTicks 1000000 --service D --lambda 100 -L 2000 -C 1000000 --size 100')

    elif args[1] == 'Q2':
        times = int(args[2])
        testList.append('./simulator.py --generation M --tickLen 0.00001 --numOfTicks 10000000 --service D --lambda 100 -L 2000 -C 1000000 --size inf')

    elif args[1] == 'Q3':
        times = int(args[2])
        lambda_list = ['150', '200', '250', '300', '350', '400']
        rho_list = ['0.3', '0.4', '0.5', '0.6', '0.7', '0.8']
        for counter in xrange(0, len(lambda_list)):
            testList.append('./simulator.py --generation M --tickLen 0.0001 --numOfTicks 10000000 --service D --lambda %s -L 2000 -C 1000000 --size inf --rho %s' % (int(lambda_list[counter]), float(rho_list[counter])))

    elif args[1] == 'Q3' and args[2] is not None:
        # valid start and end are 0.3 and 0.9
        start = float(args[2])
        end = float(args[3])
        times = int(args[4])

        global rhoValues
        rhoValues = numpy.arange(start, end, 0.1)
        print "[rhovals] = %s" % rhoValues

        # lambda_calc = (C * rho)/L
        for rhoval in rhoValues:
            lambda_cal = (1000000 * float(rhoval)) / 2000
            print "lambda_cal = %s" % lambda_cal
            testList.append('./simulator.py --generation M --tickLen 0.00001 --numOfTicks 10000000 --service D --lambda %s --rho %s' % (lambda_cal, rhoval))

    try:
        for repeat in xrange(0, times):
            for test in testList:
                process = subprocess.Popen(test, shell=True)
    except Exception as e:
        print "Nasty stuff took place... ~eery silence~: %s \n \
               Process returned = %s" % (e.message, process.returncode)

if __name__ == '__main__':
    main(sys.argv)
