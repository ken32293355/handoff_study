#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from calendar import c
from email.parser import BytesParser
import socket
import time
import threading
import datetime as dt
import select
import sys
import os
import queue
import subprocess
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int,
                    help="port to bind", default=3237)
args = parser.parse_args()


HOST = '192.168.1.248'
PORT = 3237
PORT2 = 3238
thread_stop = False
exit_program = False
length_packet = 250
bandwidth = 200*1000
total_time = 3600
expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec
prev_sleeptime = sleeptime
server_addr = (HOST, PORT)
thread_stop = False
exitprogram = False
pcap_path = "pcapdir"
hostname = str(PORT) + ":"

def connection(host, port, result):
    assert(result[0] == None)
    hostname = str(port) + ":"
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s_tcp.bind((host, port))
    s_udp.bind((host, port))

    udp_addr = ""

    ###
    s_udp.settimeout(0)
    while True:
        try:
            print("reading trash...")
            indata, udp_addr = s_udp.recvfrom(1024)
        except:
            break
    s_udp.settimeout(3)

    ### PHASE1 TCP connection establishment

    print(hostname, "wait for tcp connection...")
    s_tcp.listen(1)
    conn, tcp_addr = s_tcp.accept()
    print(hostname, 'tcp Connected by', tcp_addr)


    ### PHASE2 UDP1 connection establishment

    print(hostname, "wait for udp say 123...")
    try:
        indata, udp_addr = s_udp.recvfrom(1024)
    except:
        pass
    while True:
        try:
            if indata.decode() == "123":
                conn.sendall(b"PHASE2 OK")
                break

            else:
                print("get", indata.decode(), "wrong")
        except Exception as inst:
            print("Error: ", inst)
        try:
            indata, udp_addr = s_udp.recvfrom(1024)
        except Exception as inst:
            print("Error: ", inst)
    print('udp Connected by', udp_addr)
    print('udp say', indata)
    print("wait for client say OK...")

    try:
        indata = conn.recv(65535)
        if indata == b'OK':
            print(hostname, "connection setup complete")
        else:
            print("connection setup fail")
            return 0
    except:
        exit(1)

    result[0] = s_tcp, s_udp, conn, tcp_addr, udp_addr 


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

def transmision(s_udp1, s_udp2, udp_addr1, udp_addr2):
    global thread_stop
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
    thread_stop = True
    print("transmit", i, "packets")

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


while not exitprogram:

    now = dt.datetime.today()
    n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
    tcpproc1 =  subprocess.Popen(["tcpdump -i any port %s -w %s/%s_%s.pcap&"%(PORT, pcap_path,PORT, n)], shell=True)
    tcpproc2 =  subprocess.Popen(["tcpdump -i any port %s -w %s/%s_%s.pcap&"%(PORT2, pcap_path,PORT2, n)], shell=True)
    time.sleep(2)
    # s_tcp1, s_udp1, conn1, tcp_addr1, udp_addr1 = connection()
    # s_tcp2, s_udp2, conn2, tcp_addr2, udp_addr2 = connection()
    result1 = [None]
    result2 = [None]
    connection_t1 = threading.Thread(target = connection, args = (HOST, PORT, result1))
    connection_t2 = threading.Thread(target = connection, args = (HOST, PORT2, result2))
    try:
        connection_t1.start()
        connection_t2.start()
        connection_t1.join()
        connection_t2.join()
        s_tcp1, s_udp1, conn1, tcp_addr1, udp_addr1 = result1[0]
        s_tcp2, s_udp2, conn2, tcp_addr2, udp_addr2 = result2[0]
    except Exception as inst:
        print("Error: ", inst)
        tcpproc1.terminate()
        tcpproc2.terminate()
        continue
    print("connect two UE suceed")
    conn1.sendall(b"START")
    conn2.sendall(b"START")
    thread_stop = False
    t4 = threading.Thread(target = transmision, args = (s_udp1, s_udp2, udp_addr1, udp_addr2))
    t5 = threading.Thread(target = bybass_rx, args = (s_udp1))
    t6 = threading.Thread(target = bybass_rx, args = (s_udp2))
    t2 = threading.Thread(target = remote_control, args = (conn1, t4))
    t3 = threading.Thread(target = remote_control, args = (conn2, t4))
    t4.start()
    t2.start()
    t3.start()
    t5.start()
    t6.start()
    t3.join()
    t2.join()
    t4.join()
    t5.join()
    t6.join()
    s_tcp1.close()
    s_tcp2.close()
    s_udp1.close()
    s_udp2.close()
    conn1.close()
    conn2.close()
    tcpproc1.terminate()
    tcpproc2.terminate()

