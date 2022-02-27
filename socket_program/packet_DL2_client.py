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


if not hasattr(socket, 'SO_BINDTODEVICE'):
    socket.SO_BINDTODEVICE = 25

HOST = '140.112.20.183'
PORT = 3237
server_addr = (HOST, PORT)
thread_stop = False
exitprogram = False

buffer = queue.Queue()


def connection_setup():
    error_count = 0
    interface1 = 'usb0'
    interface2 = 'usb1'
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.connect((HOST, PORT))
    s_tcp.settimeout(2)
    s_udp1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("wait for bind to usb0...")
    s_udp1.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, ((interface1)+'\0').encode())
    s_udp2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("wait for bind to usb1...")
    s_udp2.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, ((interface2)+'\0').encode())

    print("wait for establish usb1 connection...")
    s_udp1.settimeout(1)
    s_udp1.sendto("123".encode(), server_addr) # Required! don't comment it
    indata = ""
    try:
        indata = s_tcp.recv(65535)
    except Exception as inst:
        print("Error: ", inst)
        error_count += 1

    while True:
        try:
            if indata == b'PHASE2 OK':
                print("PHASE2 OK")
                break

        except Exception as inst:
            print("Error: ", inst)
            error_count += 1

        try:
            s_udp1.sendto("123".encode(), server_addr) # Required! don't comment it
            indata = s_tcp.recv(65535)


        except Exception as inst:
            print("Error: ", inst)
            error_count += 1
        if error_count > 5:
            exit()


    print("wait for establish usb2 connection...")

    s_udp2.settimeout(1)

    s_udp2.sendto("456".encode(), server_addr2) # Required! don't comment it
    try:
        indata = s_tcp.recv(65535)

    except Exception as inst:
        print("Error: ", inst)

    while True:
        try:
            if indata == b'PHASE3 OK':
                print("PHASE3 OK")
                break
            else:
                print("indata = ", indata)
        except Exception as inst:
            print("Error: ", inst)
            error_count += 1


        print("wait for establish usb2 connection...")
        try:
            s_udp2.sendto("456".encode(), server_addr2) # Required! don't comment it
            indata = s_tcp.recv(65535)
        except Exception as inst:
            print("Error: ", inst)
            error_count += 1
        if error_count > 5:
            exit()

    print("connection_setup complete")
    s_tcp.sendall(b"OK")
    return s_tcp, s_udp1, s_udp2
    
def bybass_rx(s_udp):
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

    s_tcp.close()
    s_udp.close()


while not exitprogram:
    try:
        x = input("Press Enter to start\n")
        if x == "EXIT":
            break
        now = dt.datetime.today()
        n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
        # os.system("tcpdump -i any net 140.112.20.183 -w %s.pcap &"%(n))
        s_tcp, s_udp1, s_udp2 = connection_setup()
    except Exception as inst:
        print("Error: ", inst)
        # os.system("pkill tcpdump")
        continue
    thread_stop = False
    t1 = threading.Thread(target=bybass_rx, args=(s_udp1, ))
    t2 = threading.Thread(target=bybass_rx, args=(s_udp2, ))
    t1.start()
    t2.start()
    while True and t1.is_alive() and t2.is_alive():
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
    t1.join()
    t2.join()
    s_tcp.close()
    s_udp1.close()
    s_udp2.close()

    # os.system("pkill tcpdump")
