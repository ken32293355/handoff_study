import os
import sys
import datetime as dt
import time, subprocess



if __name__ == '__main__':
    os.system("echo wmnlab | sudo -S su")
    t = dt.datetime.today()
    n = '-'.join([str(x) for x in[ t.year, t.month, t.day, t.hour, t.minute, t.second]])

    # print(len(sys.argv))
    # print(sys.argv)
    print("All supported port: 3200-3300, odd number for Uplink, even number for Downlink. ")
    print("------------------------------")
    print("You may type: ")
    print("(1) \'python3 iperf_server.py start 3231\'")
    print("     to open port 3231-3232. ")
    print("(2) \'python3 iperf_server.py start 3235 3237 3231\'")
    print("     to open port 3231-3232 & 3235-3238. ")
    print("------------------------------")

    # dirname = os.path.abspath(os.path.dirname(__file__))
    try: 
        os.mkdir(os.path.join('..', 'tcpdump'))
        os.mkdir(os.path.join('..', 'serverlog'))
    except: 
        pass

    _l = []
    run_list = []
    
    if len(sys.argv) == 1: 
        print("Error: Please specify \'start\' or \'stop\'. ")
    elif len(sys.argv) == 2: 
        print("Error: Please specify port numbers")
    else: 
        if sys.argv[1] == 'start': 
            for i in range(2, len(sys.argv)): 
                _l.append('iperf3 -s -B 0.0.0.0 -p {} -V --logfile '.format(int(sys.argv[i]))   + os.path.join('..', 'serverlog', n + '_serverLog_{}_UL.log'.format(int(sys.argv[i]))  ))
                _l.append('iperf3 -s -B 0.0.0.0 -p {} -V --logfile '.format(int(sys.argv[i])+1) + os.path.join('..', 'serverlog', n + '_serverLog_{}_DL.log'.format(int(sys.argv[i])+1)))
            
            for i in range(2, len(sys.argv)): 
                _l.append('sudo tcpdump port {} -w '.format(int(sys.argv[i]))   + os.path.join('..', 'tcpdump', n + '_serverDump_{}_UL.pcap'.format(int(sys.argv[i]))  ))
                _l.append('sudo tcpdump port {} -w '.format(int(sys.argv[i])+1) + os.path.join('..', 'tcpdump', n + '_serverDump_{}_DL.pcap'.format(int(sys.argv[i])+1)))
            for l in _l: 
                print(l)
                run_store = subprocess.Popen(l.split(" "), preexec_fn=os.setpgrp)
                run_list.append(run_store)
                
            while True:
                time.sleep(3)
                s = input("Enter \'STOP\' to stop: ")
                time.sleep(0.1)
                if s == 'STOP':
                    break
            
            for run_item in run_list:
                try:
                    print(run_item, ", PID: ", run_item.pid)
            
                    pgid = os.getpgid(run_item.pid)
                    
                    command = "sudo kill -9 -{}".format(pgid)
                    subprocess.check_output(command.split(" "))
                except Exception as e:
                    print(e)
        else: 
            print("Error: You can only specify \'start\' followed with a list of specified ports. ")


