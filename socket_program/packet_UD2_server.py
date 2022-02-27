#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ast import While
from calendar import c
import socket
import time
import threading
import datetime as dt
import select
import sys
import os
import queue

HOST = '192.168.1.248'
PORT = 3237
PORT2 = 3238
thread_stop = False
exit_program = False
length_packet = 250
bandwidth = 20000*1000
total_time = 10
expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec
prev_sleeptime = sleeptime
server_addr = (HOST, PORT)
thread_stop = False
exitprogram = False
pcap_path = "pcapdir"
def connection():
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_udp1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_udp2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s_tcp.bind((HOST, PORT))
    s_udp1.bind((HOST, PORT))
    s_udp2.bind((HOST, PORT2))
    s_udp1.settimeout(2)
    s_udp2.settimeout(2)
    print('server start at: %s:%s' % (HOST, PORT))

    ### PHASE1 TCP connection establishment

    print("wait for tcp connection...")
    s_tcp.listen(1)
    conn, tcp_addr = s_tcp.accept()
    print('tcp Connected by', tcp_addr)


    ### PHASE2 UDP1 connection establishment

    print("wait for udp1 say 123...")
    try:
        indata, udp_addr1 = s_udp1.recvfrom(1024)
    except:
        pass
    while True:
        try:
            if indata.decode() == "123":
                conn.sendall(b"PHASE2 OK")
                break
        except:
            pass
        indata, udp_addr1 = s_udp1.recvfrom(1024)
    
    print('udp1 Connected by', udp_addr1)
    print('udp1 say', indata)


    ### PHASE3 UDP2 connection establishment


    print("wait for udp2 say 456...")
    try:
        indata, udp_addr2 = s_udp2.recvfrom(1024)
    except:
        pass
    while True:
        try:
            if indata.decode() == "456":
                conn.sendall(b"PHASE3 OK")
                break
            else:
                print("udp2 get", indata)
        except:
            pass
        try:
            print("wait for udp2 say 456...")
            indata, udp_addr2 = s_udp2.recvfrom(1024)
        except:
            pass
    print('udp2 Connected by', udp_addr2)
    print('udp2 say', indata)
    try:
        indata = conn.recv(65535)
        if indata == b'OK':
            print("connection setup complete")
        else:
            print("connection setup fail")
            return 0
    except:
        exit(1)
    return s_tcp, s_udp1, s_udp2, conn, tcp_addr, udp_addr1, udp_addr2

def remote_control(conn, t):
    global thread_stop
    global exit_program
    while t.is_alive():
        try:
            print("waiting for stopping")
            indata, addr = conn.recvfrom(1024)
            print('recvfrom ' + str(addr) + ': ' + indata.decode())
            if not indata or indata.decode() == "STOP" or not addr:
                thread_stop = True
                break
            elif indata.decode() == "EXIT":
                thread_stop = True
                exit_program = True
                break
        except Exception as inst:
            print("Error: ", inst)
    print("STOP remote control")
def bybass_rx(s_udp):
    s_udp.settimeout(3)
    print("wait for indata...")
    i = 0
    start_time = time.time()
    count = 1
    seq = 0
    prev_capture = 0
    prev_loss = 0
    global thread_stop
    while not thread_stop:
        try:
            indata, addr = s_udp.recvfrom(1024)
            if len(indata) != 250:
                print("WTF len", len(indata))
            seq = int(indata[16:24].hex(), 16)
            ts = int(int(indata[0:8].hex(), 16)) + float("0." + str(int(indata[8:16].hex(), 16)))
            # print(dt.datetime.fromtimestamp(time.time())-dt.datetime.fromtimestamp(ts)-dt.timedelta(seconds=0.28))
            # s_local.sendall(indata)
            ok = int(indata[24:25].hex(), 16)
            # buffer.put(indata)
            if ok == 0:
                break
            else:
                i += 1
            if time.time()-start_time > count:
                print("[%d-%d]"%(count-1, count), "capture", i-prev_capture, "loss", seq-i+1-prev_loss, sep='\t')
                prev_loss += seq-i+1-prev_loss
                count += 1
                prev_capture = i
        except Exception as inst:
            print("Error: ", inst)
    thread_stop = True
    print("[%d-%d]"%(count-1, count), "capture", i-prev_capture, "loss", seq-i+1-prev_loss, sep='\t')
    print("---Experiment Complete---")
    print("Total capture: ", i, "Total lose: ", seq - i + 1)
    print("STOP bypass")



def transmision(s_udp1, s_udp2, udp_addr1, udp_addr2):
    print("start transmision to addr:%s and addr:%s"%(udp_addr1, udp_addr2))
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
        s_udp1.sendto(outdata, udp_addr1)
        s_udp2.sendto(outdata, udp_addr2)
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
    s_udp1.sendto(outdata, udp_addr1)
    s_udp2.sendto(outdata, udp_addr2)

    print("transmit", i, "packets")



while not exitprogram:

    now = dt.datetime.today()
    n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
    os.system("echo wmnlab | sudo -S pkill tcpdump")
    os.system("echo wmnlab | sudo -S tcpdump -i any port 3237 -w %s/%s.pcap&"%(pcap_path, n))
    time.sleep(2)
    s_tcp, s_udp1, s_udp2, conn, tcp_addr, udp_addr1, udp_addr2 = connection()
    thread_stop = False
    t = threading.Thread(target = bybass_rx, args = (s_udp1,))
    t2 = threading.Thread(target = remote_control, args = (conn, t))
    t3 = threading.Thread(target = bybass_rx, args = (s_udp2,))
    t4 = threading.Thread(target = transmision, args = (s_udp1, s_udp2, udp_addr1, udp_addr2))
    t.start()
    t2.start()
    t3.start()
    t4.start()
    
    t.join()
    t3.join()
    t2.join()
    t4.join()
    s_tcp.close()
    s_udp1.close()
    s_udp2.close()
    conn.close()
    os.system("echo wmnlab | sudo -S pkill tcpdump")
