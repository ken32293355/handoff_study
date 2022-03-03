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
server_addr = (HOST, PORT)

thread_stop = False
exit_program = False
length_packet = 250
bandwidth = 200*1000
total_time = 3600
expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec
prev_sleeptime = sleeptime
pcap_path = "pcapdir"
exitprogram = False
def connection_setup():
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_tcp.connect((HOST, PORT))
    # s_udp.sendto("123".encode(), server_addr) # Required! don't comment it

    s_udp.settimeout(0)

    print("wait for establish udp connection...")
    s_udp.settimeout(1)
    s_udp.sendto("123".encode(), server_addr) # Required! don't comment it
    indata = ""
    try:
        indata = s_tcp.recv(65535)
    except Exception as inst:
        print("Error: ", inst)

    while True:
        try:
            if indata == b'PHASE2 OK':
                print("PHASE2 OK")
                break

        except Exception as inst:
            print("Error: ", inst)

        try:
            s_udp.sendto("123".encode(), server_addr) # Required! don't comment it
            indata = s_tcp.recv(65535)


        except Exception as inst:
            print("Error: ", inst)

    print("connection_setup complete")
    s_tcp.sendall(b"OK")


    return s_tcp, s_udp

def transmision(s_udp):
    print("start transmision to addr", s_udp)
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
        s_udp.sendto(outdata, server_addr)
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
    s_udp.sendto(outdata, server_addr)

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
    thread_stop = True
    print("[%d-%d]"%(count-1, count), "capture", i-prev_capture, "loss", seq-i+1-prev_loss, sep='\t')
    print("---Experiment Complete---")
    print("Total capture: ", i, "Total lose: ", seq - i + 1)
    print("STOP bypass")

    s_tcp.close()
    s_udp.close()

if not os.path.exists(pcap_path):
    os.system("mkdir %s"%(pcap_path))



while not exitprogram:
    try:
        x = input("Press Enter to start\n")
        if x == "EXIT":
            break
        now = dt.datetime.today()
        n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
        os.system("tcpdump -i any net 140.112.20.183 -w %s/%s.pcap &"%(pcap_path,n))
        s_tcp, s_udp = connection_setup()
    except Exception as inst:
        print("Error: ", inst)
        os.system("pkill tcpdump")
        continue
    thread_stop = False
    t = threading.Thread(target=transmision, args=(s_udp, ))
    t2 = threading.Thread(target=bybass_rx, args=(s_udp, ))
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
    s_tcp.close()
    s_udp.close()

    os.system("pkill tcpdump")
