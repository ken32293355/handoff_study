"""
This code should be modified first. 
The paremeters depend on your environment.
"""

import os
import sys
import datetime as dt

if __name__ == '__main__':
    # func = sys.argv[1]
    # port = sys.argv[2]
    file= open('enable','r')
    check=file.readline()
    file.close()
    number=0
    
    if not os.path.exists("iperf3_log"):
        os.system("mkdir iperf3_log")

    while (check == 'true\n') and number < 10:
        t = dt.datetime.today()
        n = '-'.join([str(x) for x in[ t.year, t.month, t.day, t.hour, t.minute, t.second]])
        ###   Modified the parameters here      ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ ###
        cmd = r'iperf3 -c 140.112.20.183 -p 3231 -u -R -l 250 -b 200k -V -t 7200 --logfile ./iperf3_log/DL-'+ n 
        print(cmd)
        os.system(cmd)
        file= open('enable','r')
        check=file.readline()
