#!/usr/bin/python

# Script composed by Young Chen
# This script is to do the experiment outside measuring the cell information.
# Associated scripts files are MRT-test.sh iperf3 for UL/DL python files
# Extra applications are QLog of Quectel
# External HW is Solid disk


# test flow (The harddisk must be linked on the plateform.)
# 1. initialize a ramdisk directory in the /tmp 
# 2. send ATE0 to disable the echo function from module
# 3. cat the return value to a log file
# 4. QLog to /tmp/ramdisk  
# 5. periodically check the files and move them to HDD
# Output files will be
    # log: at command return value
    # file-time-log: time of qxdm files  
    # tcp-file: tcpdump file

import os
import sys
import datetime as dt
import device



if __name__ == '__main__':


    # top to monitor	
    # 
    # print(sys.argv[0])
    if (sys.argv[1] == 'set'):
        print('set')
        # sync the current time
        os.system("ntpd restart")
        t = dt.datetime.today()
        print("current time:", t)
        os.system('echo "true" > enable')
        if (not os.path.isdir('tcpdump-files')):
            os.system('mkdir tcpdump-files')		
        device.init()
        device.record()
    # start iperf testing
    if (sys.argv[1] == 'start'):
        print('start to tcpdump, iperf & QLog')
        os.system('python handover-scan.py tcp &')
        os.system('python iperf-script-UL.py &')
        os.system('python iperf-script-DL.py &')
    # start tcpdump
    if (sys.argv[1] == 'tcp'):
        t = dt.datetime.today()
        n = '-'.join([str(x) for x in[ t.year, t.month, t.day, t.hour, t.minute, t.second]])
        os.system('tcpdump net 140.112.20.183 -w tcpdump-files/' + n + ' &')
    # stop the experiment
    if(sys.argv[1] == 'stop'):
        os.system('echo "false" > enable')
        os.system('killall -9 tcpdump')
        os.system('killall -9 iperf3')

