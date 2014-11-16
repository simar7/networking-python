#!/usr/bin/python

import subprocess
from subprocess import Popen

def main():
    for counter in [1, 2, 5]:
        process = subprocess.Popen("./tester.py q%s" % (counter), shell=True)
        process.wait()
        print "test %s/3 done" % (counter)
    print "all done, kthxbai"

if __name__ == '__main__':
    main()
