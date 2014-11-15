#!/usr/bin/python

import subprocess
from subprocess import Popen

def main():
    for counter in xrange(1, 6):
        process = subprocess.Popen("./tester.py q%s" % (counter), shell=True)
        process.wait()
        print "test %s/5 done" % (counter)
    print "all done, kthxbai"

if __name__ == '__main__':
    main()
