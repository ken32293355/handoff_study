"""
This code can use moxa device command to do some function.
"""
import os
from subprocess import PIPE, run
import time
import datetime as dt
def out(command):
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    return result.stdout


# select prefered band. select LTE or NR
def init():
    z = out(r"mxat -d /dev/ttyUSB2 -c ATE1")
    print(z)
    z = out(r"mxat -d /dev/ttyUSB2 -c AT+QNWPREFCFG=\"nsa_nr5g_band\"")
    print(z)
    # z = out(r"mxat -d /dev/ttyUSB2 -c AT+QNWPREFCFG=\"lte_band\",28")
    print(z)


# record the timing and cell infomation
def record():
    f1 = open("enable")
    n = 0
    t = dt.datetime.today()
    w = '-'.join([str(x) for x in[ t.year, t.month, t.day, t.hour, t.minute, t.second]])
    f = open('./device_log/log_'+w, 'a')
    while f1.readline() == 'true\n':
        if n % 10 == 0:
            print("recording...")
        f.write('time,'+str(dt.datetime.today())+ '\n')
        z = out(r"mxat -d /dev/ttyUSB2 -c at+qeng=\"servingcell\"")
        f.write(z)
        z = out(r"mxat -d /dev/ttyUSB2 -c at+qeng=\"neighbourcell\"")
        f.write(z)
        n += 1
#        time.sleep(0.1)
        f1 = open("enable")

