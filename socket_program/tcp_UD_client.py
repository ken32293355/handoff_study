#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import time
import threading
import datetime as dt
import select
import sys
import os
import queue
import subprocess
import re

HOST = '140.112.20.183'

f = open("port.txt", "r")
l = f.readline()
PORT = int(l)
PORT2 = PORT + 1

server_addr = (HOST, PORT)

thread_stop = False
exit_program = False
length_packet = 362
bandwidth = 289.6*1000
total_time = 3600
expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec
prev_sleeptime = sleeptime
pcap_path = "pcapdir"
ss_dir = "ss"
exitprogram = False

IP_MTU_DISCOVER   = 10
IP_PMTUDISC_DONT  =  0  # Never send DF frames.
IP_PMTUDISC_WANT  =  1  # Use per route hints.
IP_PMTUDISC_DO    =  2  # Always DF.
IP_PMTUDISC_PROBE =  3  # Ignore dst pmtu.
TCP_CONGESTION = 13   # defined in /usr/include/netinet/tcp.h
cong = 'cubic'.encode()

def get_ss(port):
    now = dt.datetime.today()
    n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
    f = open(os.path.join(ss_dir, n) + '.csv', 'a+')
    while not thread_stop:
        proc = subprocess.Popen(["ss -it dst :%d"%(port)], stdout=subprocess.PIPE, shell=True)
        line = proc.stdout.readline()
        line = proc.stdout.readline()
        line = proc.stdout.readline().decode().strip()
        f.write(",".join([str(dt.datetime.now())]+ re.split("[: \n\t]", line))+'\n')
        time.sleep(1)
    f.close()


def connection_setup(host, port, result):
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.connect((host, port))
    # s_tcp.setsockopt(socket.SOL_IP, IP_MTU_DISCOVER, IP_PMTUDISC_DONT)
    s_tcp.setsockopt(socket.SOL_IP, IP_MTU_DISCOVER, IP_PMTUDISC_DO)
    s_tcp.setsockopt(socket.IPPROTO_TCP, TCP_CONGESTION, cong)
    result[0] = s_tcp
    return s_tcp

def transmision(s_tcp):
    print("start transmision to addr", s_tcp)
    i = 0
    prev_transmit = 0
    ok = (1).to_bytes(1, 'big')
    start_time = time.time()
    count = 1
    sleeptime = 1.0 / expected_packet_per_sec
    prev_sleeptime = sleeptime
    redundent = os.urandom(length_packet-12-1)

    global thread_stop
    while time.time() - start_time < total_time and not thread_stop:
        try:
            t = time.time()
            t = int(t*1000).to_bytes(8, 'big')
            z = i.to_bytes(4, 'big')
            outdata = t + z + ok +redundent
            s_tcp.sendall(outdata)
            i += 1
            time.sleep(sleeptime)
            if time.time()-start_time > count:
                count += 1
                sleeptime = prev_sleeptime / expected_packet_per_sec * (i-prev_transmit) # adjust sleep time dynamically
                prev_transmit = i
                prev_sleeptime = sleeptime
        except:
            break
    thread_stop = True
    print("---transmision timeout---")
    ok = (0).to_bytes(1, 'big')
    redundent = os.urandom(length_packet-8*3-1)
    outdata = t + z + ok +redundent
    s_tcp.sendall(outdata)

    print("transmit", i, "packets")

def receive(s_tcp):
    s_tcp.settimeout(3)
    print("wait for indata...")
    i = 0
    start_time = time.time()
    count = 1
    seq = 0
    prev_capture = 0
    prev_loss = 0
    global thread_stop
    global buffer
    recv_bytes = 0
    while not thread_stop:
        try:
            indata = s_tcp.recv(65535)
            recv_bytes += len(indata)

            if time.time()-start_time > count:
                print("[%d-%d]"%(count-1, count), recv_bytes*8/1024, "kbps")
                prev_loss += seq-i+1-prev_loss
                count += 1
                recv_bytes = 0
        except Exception as inst:
            print("Error: ", inst)
            thread_stop = True
    thread_stop = True
    print("---Experiment Complete---")
    print("STOP receiving")


if not os.path.exists(pcap_path):
    os.system("mkdir %s"%(pcap_path))

if not os.path.exists(ss_dir):
    os.system("mkdir %s"%(ss_dir))



while not exitprogram:
    # os.system("pkill tcpdump")

    try:
        x = input("Press Enter to start\n")
        if x == "EXIT":
            break
        now = dt.datetime.today()
        n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
        tcpproc =  subprocess.Popen(["tcpdump -i any net 140.112.20.183  -w %s/%s.pcap&"%(pcap_path, n)], shell=True)
        
        result1 = [None]
        result2 = [None]
        connection_t1 = threading.Thread(target = connection_setup, args = (HOST, PORT, result1))
        connection_t2 = threading.Thread(target = connection_setup, args = (HOST, PORT2, result2))
        connection_t1.start()
        connection_t2.start()
        connection_t1.join()
        connection_t2.join()
        s_tcp1 = result1[0]
        s_tcp2 = result2[0]
        assert(s_tcp1 != None)


    except Exception as inst:
        print("Error: ", inst)
        os.system("pkill tcpdump")
        continue
    thread_stop = False
    t = threading.Thread(target=transmision, args=(s_tcp2, ))
    t2 = threading.Thread(target=receive, args=(s_tcp1, ))
    t3 = threading.Thread(target=get_ss, args=(PORT, ))
    t.start()
    t2.start()
    t3.start()
    try:

        while True and t.is_alive():
            x = input("Enter STOP to Stop\n")
            if x == "STOP":
                thread_stop = True
                break
            elif x == "EXIT":
                thread_stop = True
                exitprogram = True
        thread_stop = True
        t.join()
        t2.join()
        t3.join()

    except Exception as inst:
        print("Error: ", inst)
    finally:
        thread_stop = True
        s_tcp1.close()
        s_tcp2.close()
        os.system("pkill tcpdump")
