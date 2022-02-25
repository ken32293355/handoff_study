#!/usr/bin/env python3

import socket
import time
import threading
import os
import datetime as dt

HOST = '192.168.1.248'
PORT = 3237
thread_stop = False
exit_program = False
length_packet = 250
bandwidth = 20000*1000
total_time = 60
expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec
prev_sleeptime = sleeptime

pcap_path = "pcapdir"

def connection():
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s_tcp.bind((HOST, PORT))
    s_udp.bind((HOST, PORT))
    s_tcp.listen()
    print("wait for tcp connection...")
    conn, tcp_addr = s_tcp.accept()
    print('tcp Connected by', tcp_addr)
    print("wait for udp say hi...")
    indata, udp_addr = s_udp.recvfrom(1024)
    print('udp Connected by', udp_addr)
    print('server start at: %s:%s' % (HOST, PORT))
    return s_tcp, s_udp, conn, tcp_addr, udp_addr

def remote_control(conn, t):
    global thread_stop
    global exit_program
    while t.is_alive():
        try:
            print("waiting for stopping")
            indata, addr = conn.recvfrom(1024)
            print('recvfrom ' + str(addr) + ': ' + indata.decode())
            if indata == None or indata.decode() == "STOP":
                thread_stop = True
                break
            elif indata.decode() == "EXIT":
                thread_stop = True
                exit_program = True
                break
        except Exception as inst:
            print("Error: ", inst)

def transmision(s_udp, conn, udp_addr):
    print("start transmision to addr", udp_addr)
    i = 0
    prev_transmit = 0
    ok = (1).to_bytes(1, 'big')
    start_time = time.time()
    count = 1
    sleeptime = 1.0 / expected_packet_per_sec
    prev_sleeptime = sleeptime
    while time.time() - start_time < total_time and not thread_stop:
        t = time.time()
        datetimedec = int(t)
        microsec = int(str(t - int(t))[2:10])
        z = i.to_bytes(8, 'big')
        redundent = os.urandom(250-8*3-1)
        outdata = datetimedec.to_bytes(8, 'big') + microsec.to_bytes(8, 'big') + z + ok +redundent
        s_udp.sendto(outdata, udp_addr)
        i += 1
        time.sleep(sleeptime)
        if time.time()-start_time > count:
            print("[%d-%d]"%(count-1, count), "transmit", i-prev_transmit)
            count += 1
            sleeptime = prev_sleeptime / expected_packet_per_sec * (i-prev_transmit) # adjust sleep time dynamically
            prev_transmit = i
            prev_sleeptime = sleeptime
    
    print("---transmision timeout---")


    ok = (0).to_bytes(1, 'big')
    redundent = os.urandom(250-8*3-1)
    outdata = datetimedec.to_bytes(8, 'big') + microsec.to_bytes(8, 'big') + z + ok +redundent
    s_udp.sendto(outdata, udp_addr)

    print("transmit", i, "packets")


if not os.path.exists(pcap_path):
    os.system("mkdir %s"%(pcap_path))


# os.system("kill -9 $(ps -A | grep python | awk '{print $1}')") 

while not exit_program:

    now = dt.datetime.today()
    n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
    os.system("echo wmnlab | sudo -S pkill tcpdump")
    os.system("echo wmnlab | sudo -S tcpdump -i any port 3237 -w %s/%s.pcap&"%(pcap_path, n))
    time.sleep(2)
    s_tcp, s_udp, conn, tcp_addr, udp_addr = connection()
    thread_stop = False
    t = threading.Thread(target = transmision, args = (s_udp, conn, udp_addr))
    t2 = threading.Thread(target = remote_control, args = (conn, t))
    t.start()
    t2.start()
    
    t.join()
    t2.join()
    s_tcp.close()
    s_udp.close()
    conn.close()
    os.system("echo wmnlab | sudo -S pkill tcpdump")
