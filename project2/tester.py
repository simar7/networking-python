#!/usr/bin/python
'''
    ECE 358: Computer Networks
    Project: CSMA/CD protocols
    Author:  Simarpreet Singh (s244sing@uwaterloo.ca)
             Louisa Chong (l5chong@uwaterloo.ca)

'''
import sys
import subprocess

def main(args):
    test = './simulator.py -N 3'
    process = subprocess.Popen(test, shell=True)

if __name__ == '__main__':
    main(sys.argv)
