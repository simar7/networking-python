#!/usr/bin/python
'''
     ECE 358: Computer Networks
     Project: M/D/1 and M/D/1/K Queue Simulation
     Author:  Simarpreet Singh (s244sing@uwaterloo.ca)
              Louisa Chong (l5chong@uwaterloo.ca)
'''
import subprocess

def main():
    test = './simulator.py --arrival M --service M --num 2 --size 2 --tickLen 10 --numOfTicks 10'
    process = subprocess.Popen(test, shell=True)

if __name__ == '__main__':
    main()
