"""
This file is used to transformed the iperflog to a csv file.
Note that the iperf3 command must include "-V". 
Thus we can get the timming information.

The target file must be "udp" log.

Modify the parameter <filename> to the target file's name"

"""

import pandas as pd
import datetime as dt



##################  Target file's name ##################
filename = r"C:\Users\USER\Desktop\xml\DL_0830.txt"
#########################################################

outputfile = filename+'.csv'
f2 = open(outputfile, 'w')
f = open(filename)
start_time = 0
l = f.readline()

while l:
    if "Time:" in l:
        l = l[6:]
        start_time = pd.to_datetime(l).tz_convert(None) + dt.timedelta(hours=8)
        break
    l = f.readline()


while l:
    if "[ ID] Interval" in l:
        break
    l = f.readline()

l = f.readline()
f2.write("Time,Transfer,BandWidth,Jitter,Lost,Lost_p\n")

while l:

    if "OUT OF ORDER" not in l:

        l = l.split()

        if len(l) < 12:
            break
        print(l)


        l[2] = dt.timedelta(seconds = int(l[2][:l[2].find('.')])) + start_time
        l[2] = str(l[2])
        l[10] = l[10][:l[10].find(r'/')]
        l[-1] = l[-1][1:l[-1].find(r'%')]
        l[-1] = "0" if l[-1] == 'nan' else l[-1]
        l2 = [l[2], l[4], l[6], l[8], l[10], l[-1]]
        print(l2)
        f2.write(",".join(l2)+'\n')
        
    l = f.readline()
