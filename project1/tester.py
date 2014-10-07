#!/usr/bin/python
'''
     ECE 358: Computer Networks
     Project: M/D/1 and M/D/1/K Queue Simulation
     Author:  Simarpreet Singh (s244sing@uwaterloo.ca)
              Louisa Chong (l5chong@uwaterloo.ca)
'''
import subprocess

def main():
    test = './simulator.py --generation M --tickLen 0.0000001 --numOfTicks 10000 --service D --lambda 300 -L 2000 -C 1000000 --size 10'
    process = subprocess.Popen(test, shell=True)

if __name__ == '__main__':
    main()
