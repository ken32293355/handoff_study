#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ast import While
import socket
import time
import threading
import datetime as dt
import select
import sys
import os
import queue

HOST = '140.112.20.183'
PORT = 3237
HOST2 = "192.168.1.153"  # The server's hostname or IP address
PORT2 = 3232  # The port used by the server
server_addr = (HOST, PORT)
thread_stop = False
exitprogram = False

buffer = queue.Queue()

def connection_setup():
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_tcp.connect((HOST, PORT))
    s_udp.sendto("123".encode(), server_addr) # Required! don't comment it
    s_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s_local = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # s_local.connect((HOST2, PORT2))

    return s_tcp, s_udp, s_local



def bybass_rx(s_udp, s_local):
    s_udp.settimeout(10)
    print("wait for indata...")
    i = 0
    start_time = time.time()
    count = 1
    seq = 0
    prev_capture = 0
    prev_loss = 0
    global thread_stop
    global buffer
    buffer = queue.Queue()
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


def bybass_tx(s_local):
    global buffer
    global thread_stop
    # while not thread_stop:
    #     try:
#             indata = buffer.get(timeout=5)
#             s_local.sendall(indata)
    #     except Exception as inst:
    #         print("tx error", thread_stop)
    #         print("Error: ", inst)
    print("STOP TX")
while not exitprogram:
    try:
        x = input("Press Enter to start\n")
        if x == "EXIT":
            break
        now = dt.datetime.today()
        n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
        os.system("tcpdump -i any net 140.112.20.183 -w %s.pcap &"%(n))
        s_tcp, s_udp, s_local = connection_setup()
    except Exception as inst:
        print("Error: ", inst)
        os.system("pkill tcpdump")
        continue
    thread_stop = False
    t = threading.Thread(target=bybass_rx, args=(s_udp,s_local))
    t2 = threading.Thread(target=bybass_tx, args=(s_local,))
    t.start()
    t2.start()
    while True and t.is_alive():
        x = input("Enter STOP to Stop\n")
        if x == "STOP":
            thread_stop = True
            s_tcp.sendall("STOP".encode())
            break
        elif x == "EXIT":
            thread_stop = True
            exitprogram = True
            s_tcp.sendall("EXIT".encode())
    thread_stop = True
    t.join()
    t2.join()
    s_tcp.close()
    s_udp.close()
    s_local.close()

    os.system("pkill tcpdump")
